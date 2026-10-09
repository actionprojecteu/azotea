from dataclasses import dataclass
from typing import Protocol

from azotea_cli.common.enums import BayerPattern, HeaderType
from azotea_cli.common.errors import AzoteaError

# ------------------
# Package exceptions
# ------------------


class ConsentNotAgreedError(AzoteaError):
    """Consent form was not signed or was declined"""

    pass


class LocationExistsError(AzoteaError):
    """Location already exists"""

    pass


class LocationMissingError(AzoteaError):
    """Location does not exists"""

    pass


class ObserverExistsError(AzoteaError):
    """Observer already exists"""

    pass


class ObserverMissingError(AzoteaError):
    """Observer does not exists"""

    pass


class CameraExistsError(AzoteaError):
    """Camera already exists"""

    pass


class CameraMissingError(AzoteaError):
    """Camera does not exists"""

    pass


# -----------
# Dataclasses
# -----------


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


# ----------
# Interfaces
# ----------


class IProvision(Protocol):
    def consent_view(self, agree: bool) -> None: ...
    def create_location(self, form: LocationForm, as_default: bool) -> None: ...
    def update_location(self, form: LocationForm) -> None: ...
    def create_observer_vers(self, form: ObserverForm, as_default: bool) -> None: ...
    def update_observer(self, form: ObserverForm) -> None: ...
    def create_camera(self, form: CameraForm, as_default: bool) -> None: ...
    def create_camera_from_image(self, path: str, as_default: bool) -> None: ...


__all__ = [
    "LocationForm",
    "ObserverForm",
    "CameraForm",
    "ConsentNotAgreedError",
    "LocationExistsError",
    "LocationMissingError",
    "ObserverExistsError",
    "ObserverMissingError",
    "CameraExistsError",
    "CameraMissingError",
]
