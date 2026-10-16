# ------------------
# standard libraries
# ------------------
#
import importlib.resources as resources
import logging
from datetime import datetime, timezone

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy.orm import Session


# ---------------
# Own dependecies
# ---------------

from azotea_cli.infra.sqlalchemy import Database
from azotea_cli.provision.errors import ConsentNotAgreedError
from azotea_cli.provision.ports import ConsentService
from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

class SqaConsentRepo(ConsentService):
    def __init__(self, db: Database) -> None:
        self.db = db

    def review(self) -> str:
        return text()

    def agree(self, agreed: bool) -> None:
        with self.db.session() as session:
            if agreed:
                tstamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:SZ")
                with session.begin():
                    if not self._is_signed(session):
                        config.save(session, "gdpr", "agree", "Yes")
                        config.save(session, "gdpr", "tstamp", tstamp)
                        log.info("consent form signed")

    def agreed(self) -> bool:
        with self.db.session() as session:
            return self._is_signed(session)

    def check_raises(self) -> None:
        with self.db.session() as session:
            if not self._is_signed(session):
                raise ConsentNotAgreedError

    def _is_signed(self, session: Session) -> bool:
        answer = config.load(session, "gdpr", "agree")
        return False if answer is None or answer.lower() != "yes" else True


def text() -> str:
    pkg = ".".join(__name__.split(".")[:-1])  # get the absolute parent package path
    return resources.read_text(pkg, "consent.txt", encoding="utf-8")
