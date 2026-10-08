from . import location, consent
from .location import LocationForm
from .consent import  ConsentNotAgreed

def consent_view(agree: bool) -> None:
    consent.view(agree)

def create_location(form: LocationForm) -> None:
    location.crupdate(form)

def update_location(form: LocationForm) -> None:
    location.crupdate(form)



__all__ = ["create_location", "LocationForm", "ConsentNotAgreed"]
