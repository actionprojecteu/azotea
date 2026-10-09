from dataclasses import dataclass

from azotea_cli.common.enums import BayerPattern, HeaderType

@dataclass(frozen=True)
class DefaultOpticsForm:
    focal_len: float | None
    f_number: float | None

@dataclass(frozen=True)
class DefaultOptics:
    focal_len: float
    f_number: float

@dataclass(frozen=True)
class LocationForm:
    site_name: str
    location: str
    longitude: float | None
    latitude: float | None
    utc_offset: int | None
    randomized: bool = False


@dataclass(frozen=True)
class ObserverForm:
    family_name: str
    surname: str
    affiliation: str | None
    acronym: str | None


@dataclass(frozen=True)
class CameraForm:
    model: str
    width: int
    height: int
    bias: int
    extension: str
    header_type: HeaderType
    bayer_pattern: BayerPattern
    x_pixsize: float
    y_pixsize: float

@dataclass(frozen=True)
class RoiForm:
    x1: int
    y1: int
    x2: int
    y2: int
    comment: str | None

    def __str__(self) -> str:
        return f"[{self.y1}:{self.y2},{self.x1}:{self.x2}]"

@dataclass(frozen=True)
class RectForm2:
    width: int
    height: int


__all__ = [
    "LocationForm",
    "ObserverForm",
    "CameraForm",
    "DefaultOptics",
    "RoiForm",
]
