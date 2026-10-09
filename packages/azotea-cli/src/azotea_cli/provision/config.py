# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------

from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
#
from azotea_cli.dao import Config

def load(session: Session, section: str, property: str) -> str | None:
    sql = select(Config.value).where(Config.section == section, Config.property == property)
    return session.scalars(sql).one_or_none()

def save(session: Session, section: str, property: str, value: str) -> None:
    sql = select(Config).where(Config.section == section, Config.property == property)
    prev = session.scalars(sql).one_or_none()
    if prev is not None:
        prev.value = value
        session.add(prev)
    else:
        new = Config(section=section, property=property, value=value)
        session.add(new)

__all__ = ["load", "save"]
