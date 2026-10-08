# ------------------
# standard libraries
# ------------------
from dataclasses import dataclass, field


import logging
import importlib.resources as resources

# ---------------------
# Third party libraries
# ---------------------

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from lica.sqlalchemy import sqa_logging
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

# ---------------
# Own dependecies
# ---------------

from azotea_cli.core.errors import AzoteaError
from azotea_cli.dao import Location


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
class LocationForm:
    site_name: str
    location: str
    longitude: float | None
    latitude: float | None
    utc_offset: int | None

# -------------------------------
# Create/Update location use case
# -------------------------------
def crupdate(form: LocationForm, randomize: bool) -> None:
    sql = select(Location).where(Location.site_name == form.site_name, Location.location==form.location)
    with SessionFactory() as session:
        with session.begin():
            prev_loc = session.scalars(sql).one_or_none()
            if prev_loc is None:
                log.info("adding new location '%s', '%s'", form.site_name, form.location)
                loc = Location(site_name=form.site_name, location=form.location, longitude=form.longitude, latitude=form.latitude, utc_offset=form.utc_offset, randomized=False)
                session.add(loc)
            else:
                log.info("modifying prev. location '%s', '%s'", prev_loc.site_name, prev_loc.location)
                if form.longitude is not None:
                    prev_loc.longitude=form.longitude
                if form.latitude is not None:
                    prev_loc.latitude=form.latitude
                if form.utc_offset is not None:
                    prev_loc.utc_offset=form.utc_offset
                session.add(prev_loc)
