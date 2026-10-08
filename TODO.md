* implemntar el default location y el default observer


* provisooning
  * segir con camera, a ver que tal va el rawpy a la hora de conseguir metadatos

```python
import rawpy
from datetime import datetime, timezone

def leer_metadata_raw(path):
    with rawpy.imread(path) as raw:
        other = raw.other

        fecha = None
        if other.timestamp:
            fecha = datetime.fromtimestamp(
                other.timestamp,
                tz=timezone.utc
            )

        return {
            "make": raw.camera_make,
            "model": raw.camera_model,
            "iso": other.iso_speed,
            "shutter_seconds": other.shutter_speed,
            "aperture": other.aperture,
            "focal_length_mm": other.focal_length,
            "timestamp": other.timestamp,
            "datetime_utc": fecha,
        }

metadata = leer_metadata_raw("imagen.CR2")
print(metadata)
```
