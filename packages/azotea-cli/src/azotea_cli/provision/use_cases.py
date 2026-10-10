from .interfaces import IConsentProv, IDisplay, ILocationProv
from .models import LocationForm

def consent_view_and_agree(consent: IConsentProv, display: IDisplay, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)

def consent_check(consent: IConsentProv) -> None:
    consent.check_raises()

def create_location(consent: IConsentProv, location: ILocationProv, form: LocationForm, as_default: bool) -> None:
    consent.check_raises()
    location.create(form, as_default)


__all__ = ["consent_check", "consent_view_and_agree"]
