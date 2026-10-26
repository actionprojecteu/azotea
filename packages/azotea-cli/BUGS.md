## Bugs críticos

### 1. `RegisterImages` no captura dos errores propios

En `operation/use_cases/register.py`, `_validate()` puede lanzar `MissingCameraModelError` y `MissingExptimeError`, pero el bucle de registro solo captura `CameraMissingError`, `MissingTimestampError`, `CameraNotDefaultError` y `ReadMetadataError`. Una sola imagen sin modelo o sin tiempo de exposición aborta todo el batch en lugar de saltarse esa imagen.[^1_1]

```python
except (
    CameraMissingError,
    MissingTimestampError,
    CameraNotDefaultError,
    MissingCameraModelError,   # falta
    MissingExptimeError,       # falta
    ReadMetadataError,
) as e:
    ...
```


### 2. `--depth` por defecto rompe `azotea batch`

En `infra/cli/azotea.py`, `--depth` tiene `default=None`, pero `RegisterForm.depth` está anotado como `int` y `scan_images()` hace `current_depth > depth`. Ejecutar `azotea batch --images-dir ...` sin `--depth` lanza `TypeError: '>' not supported between instances of 'int' and 'NoneType'`.[^1_1]

Además, `--images-dir` también tiene `default=None`; sin él, `scan_images(None, ...)` fallará al resolver el path. Debe ser obligatorio o validarse antes.[^1_1]

### 3. Doble `commit()` en `SqaImagesRepo._save_one_by_one`

En `operation/adapters/sqa/images.py`:

```python
with session.begin():
    session.add(self._translate(image))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
```

`with session.begin()` ya hace commit al salir del bloque. El `session.commit()` explícito cierra la transacción y el context manager intentará cerrar/confirmar de nuevo; tras un `rollback()`, la salida del contexto también es inconsistente. Elimina el `commit()`/`rollback()` explícitos y deja que `with session.begin()` gestione la transacción.[^1_1]

### 4. `_update()` no persiste los cambios

En `SqaImagesRepo._update()` se modifican `existing.name` y `existing.directory`, pero la sesión se abre sin `session.begin()` ni `commit()`:

```python
with self.db.session() as session:
    ...
    existing.name = image.name
    existing.directory = image.directory
    session.add(existing)
```

Al cerrar la sesión sin transacción confirmada, las rutas corregidas probablemente se pierden. Envuelve el bloque en `with session.begin():`.[^1_1]

### 5. `return` en vez de `continue` en `_update()`

Dentro del bucle:

```python
if existing is None:
    log.warning(...)
    return
```

Esto abandona todo el proceso de actualización al encontrar la primera imagen cuyo hash no existe, en vez de continuar con las restantes. Debe ser `continue`.[^1_1]

### 6. `TimeIterator` puede entrar en bucle infinito

En `infra/cli/schema.py`, `TimeIterator` termina sólo cuando `self.current == self.limit`. Si `--seconds` no divide exactamente 86 400 —por ejemplo, 7 segundos—, el iterador salta el límite y nunca se detiene. Usa:

```python
if x >= self.limit:
    raise StopIteration
```

También conviene validar que `86400 % step_seconds == 0`.[^1_1]

### 7. `camera switch` no tiene handler

En `azotool.py`, el subcomando `camera switch` se declara y añade `--model`, pero no hay `set_defaults(func=...)` ni función CLI asociada. Al ejecutarlo, `args.func` será `None` y `cli_main()` fallará con `TypeError: 'NoneType' object is not callable`.[^1_1]

## Bugs funcionales importantes

### 8. `time_id` supone resolución de 1 segundo

`SqaImagesRepo.date_time_ids()` genera siempre:

```python
time_id = int(tstamp.strftime("%H%M%S"))
```

Pero `azoschema time --seconds N` permite poblar `time_t` con pasos mayores de 1 segundo. Con `--seconds 2`, un timestamp con segundo impar —por ejemplo, `00:00:01`— produce un `time_id` inexistente y violará la FK hacia `time_t`. O fijas la resolución a 1 segundo, o calculas el ID redondeando al paso configurado.[^1_1]

### 9. `--publish` se acepta pero no hace nada

En `azotea batch`, la opción `--publish` se declara y la documentación la usa, pero `cli_batch()` sólo comprueba `--only-publish`; en el camino normal ejecuta registro y estadísticas y ignora `--publish` silenciosamente. Además, `--only-publish` lanza `NotImplementedError`, que no es `AzoteaError`, por lo que escapará como traceback en vez del manejo de errores previsto.[^1_1]

### 10. El filtro de imágenes pendientes incluye calibraciones

`pending_processing_by()` selecciona cualquier imagen sin fila en `sky_brightness_t`, sin filtrar por `ImageType.LIGHT`. Tras registrar bias, darks y flats, `ComputeSkyStatistics` intentará medir “cielo” también sobre ellos. Filtra por `imagetype == ImageType.LIGHT` y, probablemente, por `flagged == False`.[^1_1]

### 11. Deduplicación de ficheros por `set` pierde orden y puede no detectar duplicados

En `RegisterImages.execute()`:

```python
newfiles = list(set(inputfiles) - set(storedfiles))
```

- Pierde el orden determinista que produce `scan_images()`; el orden de procesado será arbitrario entre ejecuciones.[^1_1]
- Compara rutas textuales: `scan_images()` devuelve rutas resueltas absolutas, mientras que `get_stored_image_paths()` reconstruye `os.path.join(directory, name)`. Si `directory` se guardó relativo, con otro prefijo o con separadores distintos, la comparación falla y las imágenes se procesan otra vez. Normaliza ambas partes con `Path.resolve()` antes de comparar.[^1_1]


### 12. `scan_non_empty_dirs()` no poda el recorrido

`os.walk()` recorre el árbol completo aunque `depth` sea 0; el filtro posterior sólo descarta resultados. Para árboles grandes es un problema de rendimiento, y el cálculo con `split(os.sep)` es frágil con rutas absolutas y separadores. `scan_images()` sí poda `_dir_names`, pero el otro escáner no.[^1_1]

## Problemas de esquema y arranque

### 13. `azoschema` mezcla DDL y datos en una transacción

En `schema.py`:

```python
with db.engine.begin():
    Model.metadata.drop_all(bind=db.engine)
    Model.metadata.create_all(bind=db.engine)
    args.func(args)
```

`args.func()` abre sus propias sesiones y transacciones mientras la transacción externa sigue abierta. En SQLite es una receta para `database is locked`; además, `drop_all()`/`create_all()` con DDL dentro de una transacción no es portátil. Haz el reinicializado y la carga de dimensiones en fases separadas.[^1_1]

### 14. Inconsistencia de columna `height` / `length`

El modelo ORM define `Camera.height`, pero la migración de datos crea la columna `length` en `camera_t`. Aunque la lógica de migración queda excluida, esta discrepancia afecta al esquema vivo: `Model.metadata.create_all()` creará `height`, mientras los datos migrados esperan `length`. Unifica el nombre en el modelo, la vista y las consultas.[^1_1]

### 15. Versión de base de datos inconsistente

`cli_populate_config()` escribe `version = "03"`, mientras la documentación y ejemplos históricos muestran `Database version = 01`. No es un fallo de ejecución, pero puede romper comprobaciones futuras de versión si algún componente compara contra `"01"`.[^1_1]

## Problemas menores

- `configure publishing` exige `--url`, pero el ejemplo del README ejecuta el comando sin `--url`; el comando fallará tal como está documentado.[^1_1]
- La contraseña de publicación se guarda en claro en `config_t`; al menos no debería quedar en logs ni en exportaciones.[^1_1]
- `strftime("%A")`, `%a`, `%B` y `%b` dependen de la configuración regional del proceso; la tabla de fechas puede quedar en español o inglés según el entorno. Fija `locale` o genera los nombres desde datos propios.[^1_1]
- `db = DcplDatabase("DATABASE_URL")` se construye a nivel de módulo en tres CLIs; eso acopla la importación a la existencia de la variable de entorno y dificulta tests. Créalo dentro de `main()`/`cli_main()`.[^1_1]
- Los nombres de informe usan sólo `surname`; dos observadores con el mismo apellido sobrescribirán o colisionarán en los CSV. Incluye también `name` o el `observer_id`.[^1_1]


## Prioridad sugerida

1. Corregir las excepciones no capturadas en `RegisterImages` y el `--depth=None`.
2. Arreglar la transacción y el `return` de `SqaImagesRepo`.
3. Decidir y aplicar una única resolución temporal para `time_id`.
4. Filtrar `LIGHT` antes de calcular estadísticas.
5. Implementar o eliminar explícitamente `--publish` / `--only-publish`.
6. Añadir handler a `camera switch` y resolver `height` vs. `length`.

<div align="center">⁂</div>

[^1_1]: dumppy.txt
