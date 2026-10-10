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
from azotea_cli.infra.sqlalchemy import Observer

from . import config
from ..errors import (
    ObserverExistsError,
    ObserverMissingError,
    MissingDefaultObserverError,
)
from ..models import ObserverForm
from ..interfaces import ObserverProv

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------

class ObserverProvImpl(ObserverProv):

    def set_default(self, observer_id) -> None:
        with SessionFactory() as session:
            with session.begin():
                config.save(session, "observer", "observer", str(observer_id))


    def get_default(self) -> int:
        with SessionFactory() as session:
            observer_id = config.load(session, "observer", "observer")
            if observer_id is None:
                raise MissingDefaultObserverError
            return int(observer_id)

    def create_versioned(self, form: ObserverForm, as_default: bool) -> int:
        sql = select(Observer).where(
            Observer.family_name == form.family_name,
            Observer.surname == form.surname,
            Observer.valid_state == ValidState.CURRENT,
        )
        with SessionFactory() as session:
            try:
                with session.begin():
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
                        session.flush()  # Ejecuta el INSERT y carga la PK en loc.id
                        observer_id = obs.observer_id
                        log.info("created brand new observer: %s", form)
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
                        session.flush()  # Ejecuta el INSERT y carga la PK en loc.id
                        observer_id = obs.observer_id
                        log.info("create a new version with id %d of observer: %s", observer_id, form)
                    else:
                         observer_id = prev_obs.observer_id
                    if as_default:
                        log.info("saving default observer_id: %d", form, observer_id)
                        config.save(session, "observer", "observer_id", str(observer_id))
                    return observer_id
            except IntegrityError:
                raise ObserverExistsError(f"{form.family_name} {form.surname}")


    def update(self, form: ObserverForm) -> None:
        sql = select(Observer).where(
            Observer.family_name == form.family_name,
            Observer.surname == form.surname,
            Observer.valid_state == ValidState.CURRENT,
        )
        with SessionFactory() as session:
            with session.begin():
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
