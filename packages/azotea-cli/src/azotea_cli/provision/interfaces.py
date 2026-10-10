from typing import Protocol

from .models import (
    CameraForm,
    DefaultOptics,
    DefaultOpticsForm,
    LocationForm,
    ObserverForm,
    RoiForm,
)

# ----------
# Interfaces
# ----------


class IConsentProv(Protocol):
    def view(self) -> None: ...
    def agree(self, agreed: bool) -> None: ...
    def check(self) -> None: ...


class IObserverProv(Protocol):
    def create_observer_vers(self, form: ObserverForm, as_default: bool) -> None: ...
    def update_observer(self, form: ObserverForm) -> None: ...


class ILocationProv(Protocol):
    def create_location(self, form: LocationForm, as_default: bool) -> None: ...
    def update_location(self, form: LocationForm) -> None: ...


class ICameraProv(Protocol):
    def create_camera(self, form: CameraForm, as_default: bool) -> None: ...
    def create_camera_from_image(self, path: str, as_default: bool) -> None: ...


class IOpticsProv(Protocol):
    def save_default_optics(self, form: DefaultOpticsForm) -> None: ...
    def load_default_optics(self) -> DefaultOptics: ...


class IRoiProv(Protocol):
    def create_roi(self, form: RoiForm, as_default: bool) -> None: ...
    def create_roi_from_image(self, path: str,  width: int, height: int, as_default: bool) -> None: ...


__all__ = [
    "IConsentProv",
    "ILocationProv",
    "IObserverProv",
    "ICameraProv",
]
