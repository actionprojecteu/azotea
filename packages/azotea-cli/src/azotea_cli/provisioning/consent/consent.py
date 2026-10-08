# ------------------
# standard libraries
# ------------------
#
import importlib.resources as resources
import logging
from datetime import datetime, timezone

from lica.sqlalchemy import sqa_logging
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.orm import Session

# ---------------
# Own dependecies
# ---------------
from azotea_cli.core.errors import AzoteaError
from azotea_cli.dao import Config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")


class ConsentNotAgreed(AzoteaError):
    """Consent form was not signed or was declined"""


def is_signed(session: Session) -> bool:
    sql = select(Config.value).where(Config.section == "gdpr", Config.property == "agree")
    log.debug(sql)
    answer = session.scalars(sql).one_or_none()
    return False if answer is None or answer.lower() != "yes" else True

# --------------------------------------
# used by other use cases as precondition
# ---------------------------------------
def check_signed(session: Session) -> None:
    if not is_signed(session):
        raise ConsentNotAgreed
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
                tstamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:SZ")
                cfg1 = Config(section="gdpr", property="agree", value="Yes")
                cfg2 = Config(section="gdpr", property="tstamp", value=tstamp)
                session.add(cfg1)
                session.add(cfg2)
    engine.dispose()


__all__ = ["view", "check_signed", "ConsentNotAgreed"]
