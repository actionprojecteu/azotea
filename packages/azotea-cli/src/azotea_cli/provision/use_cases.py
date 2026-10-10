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
    location: ILocationProv, consent: IConsentProv, form: LocationForm, as_default: bool
) -> None:
    consent.check_raises()
    location.create(form, as_default)


def save_default_optics(
    optics: IOpticsProv, consent: IConsentProv, form: DefaultOpticsForm
) -> None:
    consent.check_raises()
    optics.save(form)


def load_default_optics(optics: IOpticsProv, consent: IConsentProv ) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    return data


def create_versioned_observer(
    observer: IObserverProv, consent: IConsentProv, form: ObserverForm, as_default: bool
) -> None:
    consent.check_raises()
    observer.create_versioned(form, as_default)


def update_observer(observer: IObserverProv, consent: IConsentProv, form: ObserverForm) -> None:
    consent.check_raises()
    observer.update(form)


def create_camera(
   camera: ICameraProv,  consent: IConsentProv, form: CameraForm, as_default: bool
) -> None:
    consent.check_raises()
    camera.create(form, as_default)


def create_camera_from_image(
    camera: ICameraProv, consent: IConsentProv, optics: IOpticsProv, path: str, as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    camera.create_from_image(path, default_optics, as_default)


def create_roi(roi: IRoiProv, consent: IConsentProv, form: RoiForm, as_default: bool) -> None:
    consent.check_raises()
    roi.create(form, as_default)


def create_roi_from_image(
    roi: IRoiProv, consent: IConsentProv, optics: IOpticsProv, path: str, form: RoiCenteredForm,  as_default: bool
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    roi.create_from_image(path, form, default_optics, as_default)
