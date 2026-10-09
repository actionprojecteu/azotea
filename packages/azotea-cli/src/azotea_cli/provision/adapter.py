from . import camera, consent, location, observer, optics, roi
from .interfaces import ICameraProv, ILocationProv, IObserverProv, IRoiProv
from .models import CameraForm, DefaultOptics, DefaultOpticsForm, LocationForm, ObserverForm, RoiForm


class Provision(ILocationProv, IObserverProv, ICameraProv, IRoiProv):
    def consent_view(self, agree: bool) -> None:
        consent.view(agree)

    def create_location(self, form: LocationForm, as_default: bool) -> None:
        location.create(form, as_default)

    def update_location(self, form: LocationForm) -> None:
        location.update(form)

    def create_observer_vers(self, form: ObserverForm, as_default: bool) -> None:
        observer.create_versioned(form, as_default)

    def update_observer(self, form: ObserverForm) -> None:
        observer.update(form)

    def create_camera(self, form: CameraForm, as_default: bool) -> None:
        camera.create(form, as_default)

    def create_camera_from_image(self, path: str, as_default: bool) -> None:
        camera.create_from_image(path, as_default)

    def save_default_optics(self, form: DefaultOpticsForm) -> None:
        optics.save_default(form)

    def load_default_optics(self) -> DefaultOptics:
        return optics.load_default()

    def create_roi(self, form: RoiForm, as_default: bool) -> None:
        roi.create(form, as_default)

    def create_roi_from_image(
        self, path: str, width: int, height: int, as_default: bool
    ) -> None:
        roi.create_from_image(path, width, height, as_default)
