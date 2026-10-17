# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from lica_sqa import Database

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Camera
from azotea_cli.provision.models import CameraForm
from azotea_cli.provision.ports import CameraRepo
from azotea_cli.common.reader.models import ImageMetadata
from azotea_cli.common.types import ObjId

from ...errors import (
    CameraMissingError,
    MissingDefaultCameraError,
)
from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaCameraRepo(CameraRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def set_default(self, camera_id: ObjId) -> None:
        with self.db.session() as session:
            with session.begin():
                log.info("saving default camera_id: %d", camera_id)
                config.save(session, "camera", "camera_id", str(camera_id))

    def get_default(self) -> ObjId:
        with self.db.session() as session:
            camera_id = config.load(session, "camera", "camera_id")
            if camera_id is None:
                raise MissingDefaultCameraError()
            log.info("loading default camera_id: %s", camera_id)
            return int(camera_id)

    def get_extension_by_id(self, camera_id: ObjId) -> str:
        with self.db.session() as session:
            sql = select(Camera.extension).where(Camera.camera_id == camera_id)
            extension = session.scalars(sql).one_or_none()
            if extension is None:
                raise CameraMissingError(camera_id)
            return extension

    def get_id_by_model(self, model: str) -> ObjId:
        with self.db.session() as session:
            sql = select(Camera.camera_id).where(Camera.model == model)
            camera_id = session.scalars(sql).one_or_none()
            if camera_id is None:
                raise CameraMissingError(model)
            return camera_id

    def create(self, form: CameraForm) -> ObjId:
        with self.db.session() as session:
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
                    return cam.camera_id
            except IntegrityError:
                log.warning("camera %s already exists", form.model)
                sql = select(Camera.camera_id).where(Camera.model == form.model)
                with self.db.session() as session:
                    return session.scalars(sql).one()

    def create_from_image(self, metadata: ImageMetadata) -> ObjId:
        make = "" if metadata.make is None else metadata.make
        model = metadata.model if metadata.model.startswith(make) else f"{make} {metadata.model}"
        with self.db.session() as session:
            try:
                with session.begin():
                    log.info("adding new camera from metadata: %s", metadata)
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
                    return cam.camera_id
            except IntegrityError:
                log.warning("camera %s already exists", model)
                sql = select(Camera.camera_id).where(Camera.model == model)
                with self.db.session() as session:
                    return session.scalars(sql).one()
