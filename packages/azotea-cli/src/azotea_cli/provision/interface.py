from dataclasses import dataclass
from typing import Protocol

from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.enums import HeaderType, BayerPattern

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
    bayer: BayerPattern
    x_pixsize: float
    y_pixsize: float

# ----------
# Interfaces
# ----------


class IProvision(Protocol):
    def consent_view(self, agree: bool) -> None: ...
    def create_location(self, form: LocationForm, as_default: bool) -> None: ...
    def update_location(self, form: LocationForm) -> None: ...
    def create_observer_vers(self, form: ObserverForm,  as_default: bool) -> None: ...
    def update_observer(self, form: ObserverForm) -> None: ...
    def create_camera(self, form: CameraForm) -> None: ...
    def create_camera_from_image(self, path: str) -> None: ...


__all__ = [
    "LocationForm",
    "ObserverForm",
    "ConsentNotAgreedError",
    "LocationExistsError",
    "LocationMissingError",
    "ObserverExistsError",
    "ObserverMissingError",
]
