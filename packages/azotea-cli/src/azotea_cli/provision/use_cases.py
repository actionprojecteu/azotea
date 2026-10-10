import logging

from .interfaces import IConsentProv, IDisplay, ILocationProv, IObserverProv, IOpticsProv
from .models import DefaultOptics, DefaultOpticsForm, LocationForm, ObserverForm

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


__all__ = [
    "consent_check",
    "consent_view_and_agree",
    "save_default_optics",
    "load_default_optics",
    "create_location",
]
