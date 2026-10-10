import logging

from .interfaces import (
    CameraProv,
    ConsentProv,
    Display,
    LocationProv,
    ObserverProv,
    IOpticsProv,
    RoiProv,
)
from .models import (
    CameraForm,
    RoiCenteredForm,
    DefaultOptics,
    DefaultOpticsForm,
    LocationForm,
    ObserverForm,
    RoiForm,
)

log = logging.getLogger(__name__.split(".")[-2])


def consent_view_and_agree(consent: ConsentProv, display: Display, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)


def consent_check(consent: ConsentProv) -> None:
    consent.check_raises()


def create_location(
    location: LocationProv, consent: ConsentProv, form: LocationForm, as_default: bool
) -> None:
    consent.check_raises()
    location.create(form, as_default)


def save_default_optics(
    optics: IOpticsProv, consent: ConsentProv, form: DefaultOpticsForm
) -> None:
    consent.check_raises()
    optics.save(form)


def load_default_optics(optics: IOpticsProv, consent: ConsentProv ) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    return data


def create_versioned_observer(
    observer: ObserverProv, consent: ConsentProv, form: ObserverForm, as_default: bool
) -> None:
    consent.check_raises()
    observer.create_versioned(form, as_default)


def update_observer(observer: ObserverProv, consent: ConsentProv, form: ObserverForm) -> None:
    consent.check_raises()
    observer.update(form)


def create_camera(
   camera: CameraProv,  consent: ConsentProv, form: CameraForm, as_default: bool
) -> None:
    consent.check_raises()
    camera.create(form, as_default)


def create_camera_from_image(
    camera: CameraProv, consent: ConsentProv, optics: IOpticsProv, path: str, as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    camera.create_from_image(path, default_optics, as_default)


def create_roi(roi: RoiProv, consent: ConsentProv, form: RoiForm, as_default: bool) -> None:
    consent.check_raises()
    roi.create(form, as_default)


def create_roi_from_image(
    roi: RoiProv, consent: ConsentProv, optics: IOpticsProv, path: str, form: RoiCenteredForm,  as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    roi.create_from_image(path, form, default_optics, as_default)
