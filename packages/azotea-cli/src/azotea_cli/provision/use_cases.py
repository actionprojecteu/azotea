from .interfaces import IConsentProv, IDisplay

def consent_view_and_agree(consent: IConsentProv, display: IDisplay, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)

def consent_check(consent: IConsentProv) -> None:
    consent.check_raises()

__all__ = ["consent_check", "consent_view_and_agree"]
