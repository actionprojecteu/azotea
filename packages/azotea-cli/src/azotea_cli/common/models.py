
from enum import StrEnum, IntEnum
from dataclasses import Field
from typing import Protocol, Any, ClassVar, TypeVar

# Define nuna anotacion de tipo DC que representa a cualquer dataclass
class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
DataClass = TypeVar("DataClass", bound=DataclassLike)


# -----------------
# Enumeration types
# -----------------
#
class ValidState(StrEnum):
    CURRENT = "Current"
    EXPIRED = "Expired"

class HeaderType(StrEnum):
    FITS = "FITS"
    EXIF = "EXIF"

class BayerPattern(StrEnum):
    RGGB = "RGGB"
    BGGR = "BGGR"
    GRBG = "GRBG"
    GBRG = "GBRG"

class ImageType(StrEnum):
    BIAS = "BIAS"
    DARK = "DARK"
    FLAT = "FLAT"
    LIGHT = "LIGHT"

class BayerIndex(IntEnum):
    """Indexes to bidimensional 2x2 RGB Bayer pattern, black_level_per_channel and white_levels_per_channel"""

    R = 0
    Gr = 1
    B = 2
    Gb = 3

# For the ime being ObjId is an alias
type ObjId = int
