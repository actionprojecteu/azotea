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

from ..errors import ConsentNotAgreedError

# ---------------
# Own dependecies
# ---------------
from ..interfaces import IConsentProv
from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")


class ConsentProvImpl(IConsentProv):
    def review(self) -> str:
        return text()

    def agree(self, agreed: bool) -> None:
        with SessionFactory() as session:
            if agreed:
                tstamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:SZ")
                with session.begin():
                    if not self._is_signed(session):
                        config.save(session, "gdpr", "agree", "Yes")
                        config.save(session, "gdpr", "tstamp", tstamp)
                        log.info("consent form signed")

    def agreed(self) -> bool:
        with SessionFactory() as session:
            return self._is_signed(session)

    def check_raises(self) -> None:
        with SessionFactory() as session:
            if not self._is_signed(session):
                raise ConsentNotAgreedError

    def _is_signed(self, session: Session) -> bool:
        answer = config.load(session, "gdpr", "agree")
        return False if answer is None or answer.lower() != "yes" else True


def text() -> str:
    pkg = ".".join(__name__.split(".")[:-1])  # get the absolute parent package path
    return resources.read_text(pkg, "consent.txt", encoding="utf-8")


# -------------------------------------
# Main use case: View and agree consent
# -------------------------------------


__all__ = ["ConsentProvImpl", "ConsentNotAgreed"]
