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

from azotea_cli.common.reader import get_reader

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Camera

from . import config
from ..errors import (
    CameraExistsError,
    CameraMissingError,
    FocalLenMissingError,
    FNumberMissingError,
    MissingDefaultCameraError,

)
from ..models import CameraForm, DefaultOptics
from ..interfaces import CameraProv

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------

class CameraProvImpl(CameraProv):

    def create(self, form: CameraForm, as_default: bool) -> int:
        with SessionFactory() as session:
            try:
                with session.begin():
                    log.info("adding new camera: %s", form)
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
                    session.flush()
                    camera_id = cam.camera_id
                    if as_default:
                        log.info("saving default camera_id: %d", camera_id)
                        config.save(session, "camera", "camera_id", str(cam.camera_id))
            except IntegrityError:
                raise CameraExistsError(form.model)
        return camera_id


    def create_from_image(self, path: str, optics: DefaultOptics, as_default: bool) -> int:
        with SessionFactory() as session:
            model = None
            try:
                with session.begin():
                    log.info("adding new camera from image: %s", path)
                    reader = get_reader(path)
                    _, extension = os.path.splitext(path)
                    metadata = reader.read_metadata(path, optics.focal_len, optics.f_number)
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
                    session.flush()
                    camera_id = cam.camera_id
            except IntegrityError:
                raise CameraExistsError(model)
        return camera_id

    def set_default(self, camera_id: int) -> None:
        with SessionFactory() as session:
            config.save(session, "camera", "camera_id", str(camera_id))

    def get_default(self) -> int:
        with SessionFactory() as session:
            camera_id = config.load(session, "camera", "camera_id")
            if camera_id is None:
                raise MissingDefaultCameraError
            return int(camera_id)
