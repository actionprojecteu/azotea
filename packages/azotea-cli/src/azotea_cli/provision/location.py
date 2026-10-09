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
from azotea_cli.dao import Location

from . import config, consent
from .errors import (
    ConsentNotAgreedError,
    LocationExistsError,
    LocationMissingError,
)
from .models import LocationForm

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------


def create(form: LocationForm, as_default: bool) -> None:
    with SessionFactory() as session:
        try:
            with session.begin():
                consent.check_signed(session)
                log.info("adding new location '%s', '%s'", form.site_name, form.location)
                loc = Location(
                    site_name=form.site_name,
                    location=form.location,
                    longitude=form.longitude,
                    latitude=form.latitude,
                    utc_offset=form.utc_offset,
                    randomized=form.randomized,
                )
                session.add(loc)
                if as_default:
                    session.flush()  # Ejecuta el INSERT y carga la PK en loc.id
                    config.save(session, "location", "location_id", str(loc.location_id))
        except ConsentNotAgreedError:
            raise
        except IntegrityError as e:
            raise LocationExistsError(f"({form.site_name}, {form.location})")
    engine.dispose()


def update(form: LocationForm) -> None:
    sql = select(Location).where(
        Location.site_name == form.site_name, Location.location == form.location
    )
    with SessionFactory() as session:
        with session.begin():
            consent.check_signed(session)
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
    engine.dispose()


__all__ = ["create, update"]
