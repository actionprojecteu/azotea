* Es posible que no haya que hacer flip al bayer pattern del sharpcap porque la media del canal R salen menor que la del canal B
* ver como funciona alembic
* versiones actual de azotea es 1.1.7

```
Dos puntos del proyecto actual son incompatibles con una URL remota:

* DcplDatabase("DATABASE_URL") y el troceado prefix, suffix = url.split("://") que antepone un base_dir local asumen un fichero. Con sqlite+libsql://host/?authToken=... ese Path no tiene sentido y la URL queda corrupta.

* La ruta larga (base_dir) existe para que SQLite escriba el .db junto al proyecto. Con réplica embebida sigue valiendo; con remoto hay que saltarse esa rama explícitamente.

Si el objetivo es que la herramienta funcione igual en local y en Turso, el punto de decisión debe ser el esquema de la URL (sqlite:// frente a sqlite+libsql://), no la presencia de DATABASE_URL. ¿Vas a usar Turso remoto o réplica embebida? La elección cambia si azoschema puede seguir dropeando el esquema sin protección.
```
