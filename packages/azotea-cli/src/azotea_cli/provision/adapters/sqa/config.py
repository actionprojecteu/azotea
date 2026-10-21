# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ---------------------
# Third party libraries
# ---------------------

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Config
from azotea_cli.common.errors import RepositoryError


def load(session: Session, section: str, property: str) -> str | None:
    sql = select(Config.value).where(Config.section == section, Config.property == property)
    try:
        result = session.scalars(sql).one_or_none()
    except OperationalError:
        raise RepositoryError("Create the database first with 'azoschema'")
    return result

def save(session: Session, section: str, property: str, value: str) -> None:
    sql = select(Config).where(Config.section == section, Config.property == property)
    try:
        prev = session.scalars(sql).one_or_none()
        if prev is not None:
            prev.value = value
            session.add(prev)
        else:
            new = Config(section=section, property=property, value=value)
            session.add(new)
    except OperationalError:
        raise RepositoryError("Create the database first with 'azoschema'")
