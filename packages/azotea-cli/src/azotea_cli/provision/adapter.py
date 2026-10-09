from .interface import IProvision, ObserverForm, LocationForm
from . import consent, location, observer

class Provision(IProvision):
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
