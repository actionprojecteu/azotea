import logging

from .interfaces import (
    ICameraProv,
    IConsentProv,
    IDisplay,
    ILocationProv,
    IObserverProv,
    IOpticsProv,
    IRoiProv,
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


def consent_view_and_agree(consent: IConsentProv, display: IDisplay, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)


def consent_check(consent: IConsentProv) -> None:
    consent.check_raises()


def create_location(
    consent: IConsentProv, location: ILocationProv, form: LocationForm, as_default: bool
) -> None:
    consent.check_raises()
    location.create(form, as_default)


def save_default_optics(
    consent: IConsentProv, optics: IOpticsProv, form: DefaultOpticsForm
) -> None:
    consent.check_raises()
    optics.save(form)


def load_default_optics(consent: IConsentProv, optics: IOpticsProv) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    return data


def create_versioned_observer(
    consent: IConsentProv, observer: IObserverProv, form: ObserverForm, as_default: bool
) -> None:
    consent.check_raises()
    observer.create_versioned(form, as_default)


def update_observer(consent: IConsentProv, observer: IObserverProv, form: ObserverForm) -> None:
    consent.check_raises()
    observer.update(form)


def create_camera(
    consent: IConsentProv, camera: ICameraProv, form: CameraForm, as_default: bool
) -> None:
    consent.check_raises()
    camera.create(form, as_default)


def create_camera_from_image(
    consent: IConsentProv, optics: IOpticsProv, camera: ICameraProv, path: str, as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    camera.create_from_image(path, default_optics, as_default)


def create_roi(consent: IConsentProv, roi: IRoiProv, form: RoiForm, as_default: bool) -> None:
    consent.check_raises()
    roi.create(form, as_default)


def create_roi_from_image(
    consent: IConsentProv, optics: IOpticsProv, roi: IRoiProv, path: str, form: RoiCenteredForm,  as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    roi.create_from_image(path, form, default_optics, as_default)
