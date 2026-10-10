# ------------------
# standard libraries
# ------------------

import logging
import os

# ---------------------
# Third party libraries
# ---------------------
#
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from azotea_cli.common.reader import get_reader

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Camera

from . import config, consent
from .errors import (
    CameraExistsError,
    CameraMissingError,
    ConsentNotAgreedError,
    FocalLenMissingError,
    FNumberMissingError,

)
from .models import CameraForm

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
        model = None
        try:
            with session.begin():
                consent.check_signed(session)
                def_focal_len = config.load(session, "optics", "focal_len")
                if def_focal_len is None:
                    raise FocalLenMissingError
                def_focal_len = float(def_focal_len)
                def_f_number = config.load(session, "optics", "f_number")
                if def_f_number is None:
                    raise FNumberMissingError
                def_f_number = float(def_f_number)
                log.info("adding new camera from image '%s'", path)
                reader = get_reader(path)
                _, extension = os.path.splitext(path)
                metadata = reader.read_metadata(path, def_focal_len, def_f_number)
                header_type = reader.header_type()
                model = metadata.model if metadata.model.startswith(metadata.make) else  f"{metadata.make} {metadata.model}"
                cam = Camera(
                    model=model,
                    bias=metadata.black_level,
                    extension=extension,
                    header_type=header_type,
                    bayer_pattern=metadata.bayer,
                    width=metadata.width,
                    height=metadata.height,
                )
                session.add(cam)
        except ConsentNotAgreedError:
            raise
        except IntegrityError:
            raise CameraExistsError(model)
