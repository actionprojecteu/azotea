# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.types import ObjId
from azotea_cli.infra.sqlalchemy import Database, Location
from azotea_cli.provision.models import LocationForm
from azotea_cli.provision.ports import LocationRepo

from ...errors import (
    LocationMissingError,
    MissingDefaultLocationError,
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


class SqaLocationRepo(LocationRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def set_default(self, location_id: ObjId):
        with self.db.session() as session:
            with session.begin():
                log.info("saving default location_id: %d", location_id)
                config.save(session, "location", "location_id", str(location_id))

    def get_default(self) -> ObjId:
        with self.db.session() as session:
            location_id = config.load(session, "location", "location_id")
            if location_id is None:
                raise MissingDefaultLocationError
            log.info("loading default location_id: %s", location_id)
            return int(location_id)

    def create(self, form: LocationForm) -> ObjId:
        with self.db.session() as session:
            try:
                with session.begin():
                    log.info("adding new location: %s", form)
                    loc = Location(
                        site_name=form.site_name,
                        location=form.location,
                        longitude=form.longitude,
                        latitude=form.latitude,
                        utc_offset=form.utc_offset,
                        randomized=form.randomized,
                    )
                    session.add(loc)
                    session.flush()  # Ejecuta el INSERT y carga la PK en loc.id
                    return loc.location_id
            except IntegrityError:
                log.warning("location (%s, %s) already exists", form.site_name, form.location)
                sql = select(Location.location_id).where(
                    Location.site_name == form.site_name, Location.location == form.location
                )
                with self.db.session() as session:
                    return session.scalars(sql).one()

    def update(self, form: LocationForm) -> None:
        sql = select(Location).where(
            Location.site_name == form.site_name, Location.location == form.location
        )
        with self.db.session() as session:
            with session.begin():
                prev_loc = session.scalars(sql).one_or_none()
                if prev_loc is None:
                    raise LocationMissingError(f"({form.site_name}, {form.location})")
                log.info(
                    "modifying prev. location '%s', '%s'", prev_loc.site_name, prev_loc.location
                )
                if form.longitude is not None:
                    prev_loc.longitude = form.longitude
                if form.latitude is not None:
                    prev_loc.latitude = form.latitude
                if form.utc_offset is not None:
                    prev_loc.utc_offset = form.utc_offset
                if form.randomized is not None:
                    prev_loc.randomized = form.randomized
                session.add(prev_loc)
