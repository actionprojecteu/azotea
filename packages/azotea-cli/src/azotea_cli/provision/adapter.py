from .interfaces import LocationProv, ObserverProv, CameraProv
from .models import  ObserverForm, LocationForm, CameraForm
from . import consent, location, observer, camera

class Provision(LocationProv, ObserverProv, CameraProv):
    def consent_view(self, agree: bool) -> None:
        consent.view(agree)
    def create_location(self, form: LocationForm,  as_default: bool) -> None:
        location.create(form, as_default)
    def update_location(self, form: LocationForm) -> None:
        location.update(form)
    def create_observer_vers(self, form: ObserverForm,  as_default: bool) -> None:
        observer.create_versioned(form, as_default)
    def update_observer(self, form: ObserverForm) -> None:
        observer.update(form)
    def create_camera(self, form: CameraForm,  as_default: bool) -> None:
        camera.create(form,as_default)
    def create_camera_from_image(self, path: str,  as_default: bool) -> None:
        camera.create_from_image(path, as_default)
