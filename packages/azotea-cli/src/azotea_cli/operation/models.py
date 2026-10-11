from dataclasses import dataclass
from datetime import datetime

from azotea_cli.common.models import ImageType, ObjId


@dataclass(frozen=True)
class RegisterForm:
    images_dir: str
    depth: int


@dataclass(frozen=True)
class ImageForm:
    name: str
    # Original directory path
    directory: str
    # Image hash (alternative key in fact)
    hash: bytes
    # DSLR ISO sensivity from EXIF
    iso: int | None
    # For imagers that do not have ISO (i.e CMOS astrocameras saving in FITS)
    gain: float | None
    # exposure time in seconds
    exptime: float
    # Either from image metadata or config default
    focal_length: float | None
    # Either from image metadata or config default
    f_number: float | None
    # Either BIAS, DARK, FLAT or LIGHT
    imagetype: ImageType
    # session identifier "YYYYMMDDHHMMSS"
    session: str
    # date of observation, utc
    date_obs: datetime
    # related references to other objects
    camera_id: ObjId
    observer_id: ObjId
    location_id: ObjId


@dataclass(frozen=True)
class SkyStatsForm:
    image_id: ObjId
    roi_id: ObjId

    # Sky Brightness measurements
    aver_signal_R: float
    vari_signal_R: float
    aver_signal_G1: float
    vari_signal_G1: float
    aver_signal_G2: float
    vari_signal_G2: float
    aver_signal_B: float
    vari_signal_B: float
