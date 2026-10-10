# ------------------
# standard libraries
# ------------------
#
import importlib.resources as resources
import logging
from datetime import datetime, timezone

from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy.orm import Session

from ...errors import ConsentNotAgreedError

# ---------------
# Own dependecies
# ---------------
from ...interfaces import IConsentProv
from .. import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")


class ConsentProvImpl(IConsentProv):
    def view(self) -> None:
        with SessionFactory() as session:
            with session.begin():
                if self.is_signed(session):
                    log.info("Consent already signed")
                    return
                print(text())

    def agree(self, agreed: bool) -> None:
        with SessionFactory() as session:
            if agreed:
                tstamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:SZ")
                config.save(session, "gdpr", "agree", "Yes")
                config.save(session, "gdpr", "tstamp", tstamp)

    def check(self) -> None:
        with SessionFactory() as session:
            if not self.is_signed(session):
                raise ConsentNotAgreedError
            log.info("Consent already signed")

    def is_signed(self, session: Session) -> bool:
        answer = config.load(session, "gdpr", "agree")
        return False if answer is None or answer.lower() != "yes" else True


# ---------------------------------------
# used by other use cases as precondition
# ---------------------------------------
#
def check_signed(session: Session) -> None:
    if not is_signed(session):
        raise ConsentNotAgreedError
    log.info("Consent already signed")


def text() -> str:
    pkg = ".".join(__name__.split(".")[:-1])  # get the absolute parent package path
    return resources.read_text(pkg, "consent.txt", encoding="utf-8")


# -------------------------------------
# Main use case: View and agree consent
# -------------------------------------


def view(agree: bool) -> None:
    with SessionFactory() as session:
        with session.begin():
            if is_signed(session):
                log.info("Consent already signed")
                return
            print(text())
            if agree:
                config.save(session, "gdpr", "agree", "Yes")
                tstamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:SZ")
                config.save(session, "gdpr", "tstamp", tstamp)
    engine.dispose()


__all__ = ["view", "check_signed", "ConsentNotAgreed"]
