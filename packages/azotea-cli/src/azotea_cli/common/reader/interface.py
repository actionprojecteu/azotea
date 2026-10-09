from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

import numpy as np

from azotea_cli.common.enums import BayerPattern, ImageType, HeaderType
from azotea_cli.common.rect import Rect

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


class RawPixels(Protocol):
    def r(self, section: Rect | None) -> Array2Du16: ...
    def g1(self, section: Rect | None) -> Array2Du16: ...
    def g2(self, section: Rect | None) -> Array2Du16: ...
    def b(self, section: Rect | None) -> Array2Du16: ...

    def r_black(self) -> int: ...
    def g1_black(self) -> int: ...
    def g2_black(self) -> int: ...
    def b_black(self) -> int: ...


class ImageReader(Protocol):
    def header_type(self) -> HeaderType: ...

    def read_metadata(self, path: Path | str) -> ImageMetadata:
        """returns an instance of ImageMetadata dataclass"""
        ...

    def read_pixels(self, path: Path | str) -> RawPixels:
        """returns an object that implements the RawPixels interface"""
        ...
