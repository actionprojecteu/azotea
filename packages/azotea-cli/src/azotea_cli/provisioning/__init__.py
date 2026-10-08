from . import consent, location, observer
from .consent import ConsentNotAgreed
from .location import LocationForm
from .observer import ObserverForm


def consent_view(agree: bool) -> None:
    consent.view(agree)


def create_location(form: LocationForm) -> None:
    location.crupdate(form)


def update_location(form: LocationForm) -> None:
    location.crupdate(form)


def create_vers_observer(form: ObserverForm) -> None:
    observer.crupdate(form, fix=False)


def update_observer(form: ObserverForm) -> None:
    observer.crupdate(form, fix=True)


__all__ = [
    "ConsentNotAgreed",
    "consent_view",
    "LocationForm",
    "create_location",
    "update_location",
    "ObserverForm",
    "create_vers_observer",
    "update_observer",
]
