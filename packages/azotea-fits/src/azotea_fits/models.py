from dataclasses import dataclass
from datetime import datetime

from azotea_cli.common.types import BayerPattern, ImageType

SWCREATOR = "SWCREATE"
EXTENSIONS = (".fit", ".fits", ".fts") # case-insensitive

@dataclass(frozen=True)
class FitsForm:
    camera: str | None
    bayer_pattern: BayerPattern | None
    gain: float | None
    bias: int | None
    x_pixsize: float | None
    y_pixsize: float | None
    image_type: ImageType | None
    diameter: float | None
    focal_length: float | None
    date_obs: datetime | None
    exptime: float | None

@dataclass(frozen=True)
class ScanForm:
    images_dir: str
    depth: int
