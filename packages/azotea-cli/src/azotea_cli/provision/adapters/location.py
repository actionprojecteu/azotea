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

from azotea_cli.common.models import ObjId
from azotea_cli.infra.sqlalchemy import Location, get_db_session

from ..errors import (
    LocationExistsError,
    LocationMissingError,
    MissingDefaultLocationError,
)
from ..interfaces import LocationRepo
from ..models import LocationForm
from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class LocationRepoImpl(LocationRepo):
    def set_default(self, location_id: ObjId):
        with get_db_session() as session:
            with session.begin():
                log.info("saving default location_id: %d", location_id)
                config.save(session, "location", "location_id", str(location_id))

    def get_default(self) -> ObjId:
        with get_db_session() as session:
            location_id = config.load(session, "location", "location_id")
            if location_id is None:
                raise MissingDefaultLocationError
            log.info("loading default location_id: %s", location_id)
            return int(location_id)

    def create(self, form: LocationForm) -> int:
        with get_db_session() as session:
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
                    location_id = loc.location_id
            except IntegrityError:
                raise LocationExistsError(f"({form.site_name}, {form.location})")
        return location_id

    def update(self, form: LocationForm) -> None:
        sql = select(Location).where(
            Location.site_name == form.site_name, Location.location == form.location
        )
        with get_db_session() as session:
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
