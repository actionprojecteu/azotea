from dataclasses import dataclass
from datetime import datetime

import numpy as np

from azotea_cli.common.enums import BayerPattern, ImageType

# type alias
type Array2Du16 = np.ndarray[tuple[int, int], np.dtype[np.uint16]]

@dataclass(frozen=True)
class ImageMetadata:
    width: int
    height: int
    make: str
    model: str
    exptime: float
    iso: int | None
    gain: float | None
    black_level: int | None
    bayer: BayerPattern
    imagetyp: ImageType
    timestamp: datetime | None
    focal_len: float | None
    f_numer: float | None

__all__ = ["ImageMetadata", "Array2Du16"]
