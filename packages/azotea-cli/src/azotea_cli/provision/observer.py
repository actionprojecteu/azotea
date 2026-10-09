# ------------------
# standard libraries
# ------------------

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select

# ---------------
# Own dependecies
# ---------------

from azotea_cli.core.constants import FOREVER
from azotea_cli.core.enums import ValidState
from azotea_cli.dao import Observer

from . import consent

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")


# -----------
# Dataclasses
# -----------


@dataclass(frozen=True)
class ObserverForm:
    family_name: str
    surname: str
    affiliation: str | None
    acronym: str | None


# -------------------------------
# Create/Update location use case
# -------------------------------
def crupdate(form: ObserverForm, fix: bool) -> None:
    sql = select(Observer).where(
        Observer.family_name == form.family_name,
        Observer.surname == form.surname,
        Observer.valid_state == ValidState.CURRENT
    )
    with SessionFactory() as session:
        with session.begin():
            consent.check_signed(session)
            now = datetime.now(timezone.utc)
            prev_obs = session.scalars(sql).one_or_none()
            if prev_obs is None:
                log.info("adding new observer '%s', '%s'", form.family_name, form.surname)
                obs = Observer(
                    family_name=form.family_name,
                    surname=form.surname,
                    affiliation=form.affiliation,
                    acronym=form.acronym,
                    valid_since=now,
                    valid_until=FOREVER,
                    valid_state=ValidState.CURRENT,
                )
                session.add(obs)
            elif not fix:
                log.info(
                    "modifying prev. observer '%s', '%s' (%s)",
                    prev_obs.family_name,
                    prev_obs.surname,
                    prev_obs.valid_state,
                )
                if any([form.affiliation is not None, form.acronym is not None]):
                    prev_obs.valid_until = now
                    prev_obs.valid_state = ValidState.EXPIRED
                    obs = Observer(
                        family_name=form.family_name,
                        surname=form.surname,
                        affiliation=form.affiliation,
                        acronym=form.acronym,
                        valid_since=now,
                        valid_until=FOREVER,
                        valid_state=ValidState.CURRENT,
                    )
                    session.add(prev_obs)
                    session.add(obs)
            else:
                log.info(
                    "fixing prev. observer '%s', '%s' (%s)",
                    prev_obs.family_name,
                    prev_obs.surname,
                    prev_obs.valid_state,
                )
                prev_obs.affiliation = form.affiliation
                prev_obs.acronym = form.acronym
                session.add(prev_obs)


__all__ = ["crupdate"]
