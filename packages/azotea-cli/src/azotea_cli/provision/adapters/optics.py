# ------------------
# standard libraries
# ------------------
#
import importlib.resources as resources
import logging
from datetime import datetime, timezone

from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.orm import Session

# ---------------
# Own dependecies
# ---------------

from ..interfaces import IOpticsProv
from ..errors import  FocalLenMissingError, FNumberMissingError
from ..models import DefaultOptics, DefaultOpticsForm
from . import config, consent

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")



# -------------------------------------
# Main use case: View and agree consent
# -------------------------------------

class OpticsProvImpl(IOpticsProv):

    def save(self, form: DefaultOpticsForm) -> None:
        with SessionFactory() as session:
            with session.begin():
                if form.focal_len is not None:
                    config.save(session, "optics", "focal_len", str(form.focal_len))
                if form.f_number is not None:
                    config.save(session, "optics", "f_number", str(form.f_number))
        log.info("saved default optics %s", form)

    def load(self) -> DefaultOptics:
        with SessionFactory() as session:
            with session.begin():
                focal_len = config.load(session, "optics", "focal_len")
                if focal_len is None:
                    raise FocalLenMissingError()
                f_number = config.load(session, "optics", "f_number")
                if f_number is None:
                    raise FNumberMissingError()
        data = DefaultOptics(focal_len = float(focal_len), f_number=float(f_number))
        log.info("loaded default optics %s", data)
        return data



__all__ = ["OpticsProvImpl"]
