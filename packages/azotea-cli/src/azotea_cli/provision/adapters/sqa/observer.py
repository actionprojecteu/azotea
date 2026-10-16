# ------------------
# standard libraries
# ------------------

import logging
from datetime import datetime, timezone

# ---------------------
# Third party libraries
# ---------------------
#
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.types import FOREVER, ObjId, ValidState
from azotea_cli.infra.sqlalchemy import Database, Observer
from azotea_cli.provision.models import ObserverForm
from azotea_cli.provision.ports import ObserverRepo

from ...errors import (
    MissingDefaultObserverError,
    ObserverMissingError,
)
from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaObserverRepo(ObserverRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def set_default(self, observer_id: ObjId) -> None:
        with self.db.session() as session:
            with session.begin():
                log.info("saving default observer_id: %d", observer_id)
                config.save(session, "observer", "observer", str(observer_id))

    def get_default(self) -> ObjId:
        with self.db.session() as session:
            observer_id = config.load(session, "observer", "observer")
            if observer_id is None:
                raise MissingDefaultObserverError
            log.info("loading default observer_id: %s", observer_id)
            return int(observer_id)

    def get_name(self, observer_id: ObjId) -> tuple[str, str]:
        with self.db.session() as session:
            sql = select(Observer.family_name, Observer.surname).where(
                Observer.observer_id == observer_id
            )
            result = session.execute(sql).one_or_none()
            if result is None:
                raise ObserverMissingError()
            return result

    def create_versioned(self, form: ObserverForm) -> ObjId:
        sql = select(Observer).where(
            Observer.family_name == form.family_name,
            Observer.surname == form.surname,
            Observer.valid_state == ValidState.CURRENT,
        )
        with self.db.session() as session:
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
                        log.info(
                            "create a new version with id %d of observer: %s", observer_id, form
                        )
                    else:
                        log.warning(
                            "observer (%s, %s) already exists", form.surname, form.family_name
                        )
                        observer_id = prev_obs.observer_id
                    return observer_id
            except IntegrityError as e:
                # this should never happen
                raise AzoteaError(str(e))

    def update(self, form: ObserverForm) -> None:
        sql = select(Observer).where(
            Observer.family_name == form.family_name,
            Observer.surname == form.surname,
            Observer.valid_state == ValidState.CURRENT,
        )
        with self.db.session() as session:
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
