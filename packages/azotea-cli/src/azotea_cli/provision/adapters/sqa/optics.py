# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Database
from azotea_cli.provision.errors import FNumberMissingError, FocalLenMissingError
from azotea_cli.provision.models import DefaultOptics, DefaultOpticsForm
from azotea_cli.provision.ports import OpticsRepo

from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


# -------------------------------------
# Main use case: View and agree consent
# -------------------------------------


class SqaOpticsRepo(OpticsRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, form: DefaultOpticsForm) -> None:
        with self.db.session() as session:
            with session.begin():
                if form.focal_len is not None:
                    config.save(session, "optics", "focal_len", str(form.focal_len))
                if form.f_number is not None:
                    config.save(session, "optics", "f_number", str(form.f_number))
        log.info("saved default optics %s", form)

    def load(self) -> DefaultOptics:
        with self.db.session() as session:
            with session.begin():
                focal_len = config.load(session, "optics", "focal_len")
                if focal_len is None:
                    raise FocalLenMissingError()
                f_number = config.load(session, "optics", "f_number")
                if f_number is None:
                    raise FNumberMissingError()
        data = DefaultOptics(focal_len=float(focal_len), f_number=float(f_number))
        log.info("loaded default optics %s", data)
        return data


__all__ = ["SqaOpticsRepo"]
