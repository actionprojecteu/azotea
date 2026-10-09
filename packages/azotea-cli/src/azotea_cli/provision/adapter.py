from .interface import IProvision, ObserverForm, LocationForm
from . import consent, location, observer

class Provision(IProvision):
    def consent_view(self, agree: bool) -> None:
        consent.view(agree)
    def create_location(self, form: LocationForm) -> None:
        location.create(form)
    def update_location(self, form: LocationForm) -> None:
        location.update(form)
    def create_observer_vers(self, form: ObserverForm) -> None:
        observer.create_versioned(form)
    def update_observer(self, form: ObserverForm) -> None:
        observer.update(form)
