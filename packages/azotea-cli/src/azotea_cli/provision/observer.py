# ------------------
# standard libraries
# ------------------

import logging
from datetime import datetime, timezone

# ---------------------
# Third party libraries
# ---------------------
#
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.constants import FOREVER
from azotea_cli.common.enums import ValidState
from azotea_cli.dao import Observer

from . import consent
from .interface import (
    ConsentNotAgreedError,
    ObserverExistsError,
    ObserverForm,
    ObserverMissingError,
)

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------


def create_versioned(form: ObserverForm) -> None:
    sql = select(Observer).where(
        Observer.family_name == form.family_name,
        Observer.surname == form.surname,
        Observer.valid_state == ValidState.CURRENT,
    )
    with SessionFactory() as session:
        try:
            with session.begin():
                consent.check_signed(session)
                now = datetime.now(timezone.utc)
                prev_obs = session.scalars(sql).one_or_none()
                if prev_obs is None:
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
                elif any(
                    [form.affiliation != prev_obs.affiliation, form.acronym != prev_obs.acronym]
                ):
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
        except ConsentNotAgreedError:
            raise
        except IntegrityError:
            raise ObserverExistsError(f"{form.family_name} {form.surname}")


def update(form: ObserverForm) -> None:
    sql = select(Observer).where(
        Observer.family_name == form.family_name,
        Observer.surname == form.surname,
        Observer.valid_state == ValidState.CURRENT,
    )
    with SessionFactory() as session:
        with session.begin():
            consent.check_signed(session)
            prev_obs = session.scalars(sql).one_or_none()
            if prev_obs is None:
                raise ObserverMissingError(f"({form.family_name}, {form.surname})")
            log.info(
                "fixing prev. observer '%s', '%s' (%s)",
                prev_obs.family_name,
                prev_obs.surname,
                prev_obs.valid_state,
            )
            prev_obs.affiliation = form.affiliation
            prev_obs.acronym = form.acronym
            session.add(prev_obs)


__all__ = ["create_versioned", "update"]
