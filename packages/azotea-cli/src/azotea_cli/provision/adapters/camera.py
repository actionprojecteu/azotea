# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------

from azotea_cli.infra.sqlalchemy import Camera
from azotea_cli.common.models import ObjId
from azotea_cli.common.reader.models import ImageMetadata

from ..errors import (
    CameraExistsError,
    MissingDefaultCameraError,
)
from ..interfaces import CameraProv
from ..models import CameraForm
from . import config

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
    def set_default(self, camera_id: ObjId) -> None:
        with SessionFactory() as session:
            log.info("saving default camera_id: %d", camera_id)
            config.save(session, "camera", "camera_id", str(camera_id))

    def get_default(self) -> ObjId:
        with SessionFactory() as session:
            camera_id = config.load(session, "camera", "camera_id")
            if camera_id is None:
                raise MissingDefaultCameraError
            log.info("loading default camera_id: %d", camera_id)
            return int(camera_id)

    def create(self, form: CameraForm) -> int:
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
            except IntegrityError:
                raise CameraExistsError(form.model)
        return camera_id

    def create_from_image(self, metadata: ImageMetadata) -> int:
        with SessionFactory() as session:
            model = None
            try:
                with session.begin():
                    log.info("adding new camera from metadata: %s", metadata)
                    model = (
                        metadata.model
                        if metadata.model.startswith(metadata.make)
                        else f"{metadata.make} {metadata.model}"
                    )
                    cam = Camera(
                        model=model,
                        bias=metadata.black_level,
                        extension=metadata.extension,
                        header_type=metadata.header_type,
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
