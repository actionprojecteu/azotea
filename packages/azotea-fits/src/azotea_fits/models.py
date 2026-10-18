# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from dataclasses import dataclass, field
from datetime import datetime

from lica_raw.adapters.fits import (
    APTDIA,
    BAYERPAT,
    DATE_OBS,
    EXPTIME,
    FOCALLEN,
    IMAGETYP,
    INSTRUME,
    LOG_GAIN,
    PEDESTAL,
    XPIXSIZE,
    YPIXSIZE,
)
from lica_raw import BayerPattern, ImageType


SWCREATOR = "SWCREATE"
EXTENSIONS = (".fit", ".fits", ".fts")  # case-insensitive


@dataclass(frozen=True)
class ScanForm:
    images_dir: str
    depth: int


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


FitsKeyword = tuple[str, str, str]  # (dataclass_field below, FITS keyword, value)

@dataclass(frozen=True)
class FitsData:
    camera: str = field(metadata={"fits": INSTRUME})
    bayer_pattern: str = field(metadata={"fits": BAYERPAT})
    gain: str = field(metadata={"fits": LOG_GAIN})
    bias: str = field(metadata={"fits": PEDESTAL})
    x_pixsize: str = field(metadata={"fits": XPIXSIZE})
    y_pixsize: str = field(metadata={"fits": YPIXSIZE})
    image_type: str = field(metadata={"fits": IMAGETYP})
    diameter: str = field(metadata={"fits": APTDIA})
    focal_length: str = field(metadata={"fits": FOCALLEN})
    date_obs: str = field(metadata={"fits": DATE_OBS})
    exptime: str = field(metadata={"fits": EXPTIME})
    swcreator: str = field(metadata={"fits": SWCREATOR})
