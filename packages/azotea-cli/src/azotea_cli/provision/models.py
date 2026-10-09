from dataclasses import dataclass

from azotea_cli.common.enums import BayerPattern, HeaderType

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


__all__ = [
    "LocationForm",
    "ObserverForm",
    "CameraForm",
]
