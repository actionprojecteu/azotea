# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Location

from . import config
from ..errors import (
    LocationExistsError,
    LocationMissingError,
    MissingDefaultLocationError,
)

from ..models import LocationForm
from ..interfaces import ILocationProv

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------

class LocationProvImpl(ILocationProv):
    def create(self, form: LocationForm, as_default: bool) -> int:
        with SessionFactory() as session:
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
                    if as_default:
                        log.info("saving default location_id: %d", form, location_id)
                        config.save(session, "location", "location_id", str(loc.location_id))
            except IntegrityError as e:
                raise LocationExistsError(f"({form.site_name}, {form.location})")
        return location_id



    def update(self, form: LocationForm) -> None:
        sql = select(Location).where(
            Location.site_name == form.site_name, Location.location == form.location
        )
        with SessionFactory() as session:
            with session.begin():
                prev_loc = session.scalars(sql).one_or_none()
                if prev_loc is None:
                    raise LocationMissingError(f"({form.site_name}, {form.location})")
                log.info("modifying prev. location '%s', '%s'", prev_loc.site_name, prev_loc.location)
                if form.longitude is not None:
                    prev_loc.longitude = form.longitude
                if form.latitude is not None:
                    prev_loc.latitude = form.latitude
                if form.utc_offset is not None:
                    prev_loc.utc_offset = form.utc_offset
                if form.randomized is not None:
                    prev_loc.randomized = form.randomized
                session.add(prev_loc)

    def set_default(self, location_id: int):
        with SessionFactory() as session:
            config.save(session, "location", "location_id", str(location_id))

    def get_default(self) -> int:
        with SessionFactory() as session:
            location_id = config.load(session, "location", "location_id")
            if location_id is None:
                raise MissingDefaultLocationError
            return int(location_id)




__all__ = ["LocationProvImpl"]
