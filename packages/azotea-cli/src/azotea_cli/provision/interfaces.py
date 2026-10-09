from typing import Protocol

from .models import CameraForm, LocationForm, ObserverForm

# ----------
# Interfaces
# ----------


class ConsentProv(Protocol):
    def consent_view(self, agree: bool) -> None: ...


class ObserverProv(Protocol):
    def create_observer_vers(self, form: ObserverForm, as_default: bool) -> None: ...
    def update_observer(self, form: ObserverForm) -> None: ...


class LocationProv(Protocol):
    def create_location(self, form: LocationForm, as_default: bool) -> None: ...
    def update_location(self, form: LocationForm) -> None: ...


class CameraProv(Protocol):
    def create_camera(self, form: CameraForm, as_default: bool) -> None: ...
    def create_camera_from_image(self, path: str, as_default: bool) -> None: ...


__all__ = [
    "ConsentProv",
    "LocationProv",
    "ObserverProv",
    "CameraProv",
]
