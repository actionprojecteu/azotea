## Bugs críticos

## Bugs funcionales importantes

### 9. `--publish` se acepta pero no hace nada

En `azotea batch`, la opción `--publish` se declara y la documentación la usa, pero `cli_batch()` sólo comprueba `--only-publish`; en el camino normal ejecuta registro y estadísticas y ignora `--publish` silenciosamente. Además, `--only-publish` lanza `NotImplementedError`, que no es `AzoteaError`, por lo que escapará como traceback en vez del manejo de errores previsto.[^1_1]


## Problemas de esquema y arranque

### 14. Inconsistencia de columna `height` / `length`

El modelo ORM define `Camera.height`, pero la migración de datos crea la columna `length` en `camera_t`. Aunque la lógica de migración queda excluida, esta discrepancia afecta al esquema vivo: `Model.metadata.create_all()` creará `height`, mientras los datos migrados esperan `length`. Unifica el nombre en el modelo, la vista y las consultas.[^1_1]

## Problemas menores

- `configure publishing` exige `--url`, pero el ejemplo del README ejecuta el comando sin `--url`; el comando fallará tal como está documentado.[^1_1]
- La contraseña de publicación se guarda en claro en `config_t`; al menos no debería quedar en logs ni en exportaciones.[^1_1]
- `strftime("%A")`, `%a`, `%B` y `%b` dependen de la configuración regional del proceso; la tabla de fechas puede quedar en español o inglés según el entorno. Fija `locale` o genera los nombres desde datos propios.[^1_1]
