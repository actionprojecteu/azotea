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
from sqlalchemy.orm import Session

# ---------------
# Own dependecies
# ---------------
from azotea_cli.dao import Camera

from . import config, consent
from .interface import (
    CameraExistsError,
    CameraForm,
    CameraMissingError,
    ConsentNotAgreedError,
)

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------


def create(form: CameraForm, as_default: bool) -> None:
    with SessionFactory() as session:
        try:
            with session.begin():
                consent.check_signed(session)
                log.info("adding new camera '%s'", form.model)
                cam = Camera(
                    model=form.model,
                    bias=form.bias,
                    extension=form.extension,
                    header_type=form.header_type,
                    bayer_pattern=form.bayer_pattern,
                    width=form.width,
                    height=form.height,
                    x_pixsize=form.x_pixsize,
                    y_pixsize=form.y_pixsize,
                )
                session.add(cam)
                if as_default:
                    session.flush()  # Ejecuta el INSERT y carga la PK en loc.id
                    config.save(session, "camera", "camera_id", str(cam.camera_id))
        except ConsentNotAgreedError:
            raise
        except IntegrityError:
            raise CameraExistsError(form.model)


def create_from_image(path: str, as_default: bool) -> None:
    with SessionFactory() as session:
        try:
            with session.begin():
                consent.check_signed(session)
                log.info("adding new camera from image '%s'", path)
        except ConsentNotAgreedError:
            raise
            raise
        except IntegrityError:
            raise CameraExistsError(cam.model)
