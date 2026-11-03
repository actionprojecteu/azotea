## Bugs críticos


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

He prbado a quitarlo y eso no funciona. Y aparentemente no le molesta el doble commit o doble rollback

## Bugs funcionales importantes


### 9. `--publish` se acepta pero no hace nada

En `azotea batch`, la opción `--publish` se declara y la documentación la usa, pero `cli_batch()` sólo comprueba `--only-publish`; en el camino normal ejecuta registro y estadísticas y ignora `--publish` silenciosamente. Además, `--only-publish` lanza `NotImplementedError`, que no es `AzoteaError`, por lo que escapará como traceback en vez del manejo de errores previsto.[^1_1]

### 11. Deduplicación de ficheros por `set` pierde orden y puede no detectar duplicados

En `RegisterImages.execute()`:

```python
newfiles = list(set(inputfiles) - set(storedfiles))
```

- Pierde el orden determinista que produce `scan_images()`; el orden de procesado será arbitrario entre ejecuciones.[^1_1]
- Compara rutas textuales: `scan_images()` devuelve rutas resueltas absolutas, mientras que `get_stored_image_paths()` reconstruye `os.path.join(directory, name)`. Si `directory` se guardó relativo, con otro prefijo o con separadores distintos, la comparación falla y las imágenes se procesan otra vez. Normaliza ambas partes con `Path.resolve()` antes de comparar.[^1_1]



## Problemas de esquema y arranque

### 14. Inconsistencia de columna `height` / `length`

El modelo ORM define `Camera.height`, pero la migración de datos crea la columna `length` en `camera_t`. Aunque la lógica de migración queda excluida, esta discrepancia afecta al esquema vivo: `Model.metadata.create_all()` creará `height`, mientras los datos migrados esperan `length`. Unifica el nombre en el modelo, la vista y las consultas.[^1_1]

## Problemas menores

- `configure publishing` exige `--url`, pero el ejemplo del README ejecuta el comando sin `--url`; el comando fallará tal como está documentado.[^1_1]
- La contraseña de publicación se guarda en claro en `config_t`; al menos no debería quedar en logs ni en exportaciones.[^1_1]
- `strftime("%A")`, `%a`, `%B` y `%b` dependen de la configuración regional del proceso; la tabla de fechas puede quedar en español o inglés según el entorno. Fija `locale` o genera los nombres desde datos propios.[^1_1]
