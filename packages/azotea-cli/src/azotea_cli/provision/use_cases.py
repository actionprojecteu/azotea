from .interfaces import IConsentProv

def consent_view_and_agree(consent: IConsentProv, agreed: bool) -> None:
    consent.view()
    if agreed:
        consent.agree(agreed)

def consent_check(consent: IConsentProv) -> None:
    consent.check()

__all__ = ["consent_check", "consent_view_and_agree"]
