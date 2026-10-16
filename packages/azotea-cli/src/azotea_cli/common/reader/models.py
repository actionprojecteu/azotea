from dataclasses import dataclass
from datetime import datetime

import numpy as np

from azotea_cli.common.types import BayerPattern, ImageType, HeaderType

# type alias
type IntArray2D = np.ndarray[tuple[int, int], np.dtype[np.uint16]]

@dataclass
class ImageMetadata:
    width: int
    height: int
    make: str | None
    model: str | None
    exptime: float | None
    iso: int | None
    gain: float | None
    black_level: int | None
    bayer: BayerPattern
    imagetyp: ImageType | None
    timestamp: datetime | None
    focal_len: float | None
    f_number: float | None
    header_type: HeaderType
    extension: str

    def __str__(self) -> str:
        return f"{self.model} {self.width}x{self.height}"

__all__ = ["ImageMetadata", "IntArray2D"]
