import logging

from .interfaces import IConsentProv, IDisplay, ILocationProv, IOpticsProv
from .models import DefaultOptics, DefaultOpticsForm, LocationForm

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
    log.info("default optics saved")


def load_default_optics(consent: IConsentProv, optics: IOpticsProv) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    log.info("default optics loaded")
    return data


__all__ = [
    "consent_check",
    "consent_view_and_agree",
    "save_default_optics",
    "load_default_optics",
    "create_location",
]
