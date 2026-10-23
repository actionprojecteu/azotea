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
from lica_raw import ImageMetadata, Rect

# ----------------
# Own dependencies
# ----------------
from azotea_cli.common.types import ObjId
from azotea_cli.infra.sqlalchemy import Roi
from azotea_cli.provision.errors import MissingDefaultRoiError, RoiMissingError
from azotea_cli.provision.models import RoiForm
from azotea_cli.provision.ports import RoiRepo

from . import config

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaRoiRepo(RoiRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def set_default(self, roi_id: ObjId) -> None:
        with self.db.session() as session:
            with session.begin():
                log.info("saving default roi_id: %d", roi_id.id)
                config.save(session, "roi", "roi_id", str(roi_id.id))

    def get_default(self) -> ObjId:
        with self.db.session() as session:
            roi_id = config.load(session, "roi", "roi_id")
            if roi_id is None:
                raise MissingDefaultRoiError
            log.info("loading default roi_id: %s", roi_id)
            return ObjId(int(roi_id))

    def get_as_rect(self, roi_id: ObjId) -> Rect:
        sql = select(Roi).where(Roi.roi_id == roi_id.id)
        with self.db.session() as session:
            roi = session.scalars(sql).one_or_none()
            if roi is None:
                raise RoiMissingError(roi_id)
            return Rect(roi.x1, roi.y1, roi.x2, roi.y2)

    def create(self, form: RoiForm) -> ObjId:
        with self.db.session() as session:
            try:
                with session.begin():
                    log.info("adding new roi: %s", form)
                    rect = Rect(form.x1, form.y1, form.x2, form.y2)
                    roi = Roi(
                        x1=rect.x1,
                        y1=rect.y1,
                        x2=rect.x2,
                        y2=rect.y2,
                        display_name=str(rect),
                        comment=form.comment,
                    )
                    session.add(roi)
                    session.flush()
                    return ObjId(roi.roi_id)
            except IntegrityError:
                log.warning("roi %s already exists", rect)  # pyright: ignore[reportPossiblyUnboundVariable]
                sql = select(Roi.roi_id).where(
                    Roi.x1 == rect.x1, Roi.y1 == rect.y1, Roi.x2 == rect.x2, Roi.y2 == rect.y2  # pyright: ignore[reportPossiblyUnboundVariable]
                )
                with self.db.session() as session:
                    roi_id = session.scalars(sql).one()
                    return ObjId(roi_id)

    def create_from_image(self, rect: Rect, metadata: ImageMetadata) -> ObjId:
        make = "" if metadata.make is None else metadata.make
        model = metadata.model if metadata.model.startswith(make) else f"{make} {metadata.model}"  # pyright: ignore[reportOptionalMemberAccess]
        with self.db.session() as session:
            try:
                with session.begin():
                    log.info("adding new roi from image '%s'", metadata)
                    center = rect.central
                    comment = f"ROI for {model}, centered at P={center}, width={rect.width}, height={rect.height}"
                    roi = Roi(
                        x1=rect.x1,
                        y1=rect.y1,
                        x2=rect.x2,
                        y2=rect.y2,
                        display_name=str(rect),
                        comment=comment,
                    )
                    session.add(roi)
                    session.flush()
                    return ObjId(roi.roi_id)
            except IntegrityError:
                log.warning("roi %s already exists", rect)
                sql = select(Roi.roi_id).where(
                    Roi.x1 == rect.x1, Roi.y1 == rect.y1, Roi.x2 == rect.x2, Roi.y2 == rect.y2
                )
                with self.db.session() as session:
                    roi_id = session.scalars(sql).one()
                    return ObjId(roi_id)
