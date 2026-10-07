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

def crupdate(form: LocationForm, randomize: bool) -> None:
    log.info("crupdate")
