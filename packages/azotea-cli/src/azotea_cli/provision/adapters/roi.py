# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------
#
from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.models import ObjId
from azotea_cli.common.reader.models import ImageMetadata
from azotea_cli.common.rect import Rect
from azotea_cli.infra.sqlalchemy import get_db_session, Roi

from ..errors import MissingDefaultRoiError, RoiMissingError
from ..interfaces import RoiRepo
from ..models import RoiForm
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
    def set_default(self, roi_id: ObjId) -> None:
        with get_db_session() as session:
            with session.begin():
                log.info("saving default roi_id: %d", roi_id)
                config.save(session, "roi", "roi_id", str(roi_id))

    def get_default(self) -> ObjId:
        with get_db_session() as session:
            roi_id = config.load(session, "roi", "roi_id")
            if roi_id is None:
                raise MissingDefaultRoiError
            log.info("loading default roi_id: %s", roi_id)
            return int(roi_id)

    def get_as_rect(self, roi_id: ObjId) -> Rect:
        sql = select(Roi).where(Roi.roi_id == roi_id)
        with get_db_session() as session:
            roi = session.scalars(sql).one_or_none()
            if roi is None:
                raise RoiMissingError(roi_id)
            return Rect(roi.x1, roi.y1, roi.x2, roi.y2)

    def create(self, form: RoiForm) -> ObjId:
        with get_db_session() as session:
            rect = None
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
                    return roi.roi_id
            except IntegrityError:
                log.warning("roi %s already exists", rect)
                sql = select(Roi.roi_id).where(Roi.x1 == rect.x1, Roi.y1 == rect.y1, Roi.x2 == rect.x2,Roi.y2 == rect.y2)
                with get_db_session() as session:
                    return session.scalars(sql).one()


    def create_from_image(self, rect: Rect, metadata: ImageMetadata) -> ObjId:
        model = (
            metadata.model
            if metadata.model.startswith(metadata.make)
            else f"{metadata.make} {metadata.model}"
        )
        with get_db_session() as session:
            try:
                with session.begin():
                    log.info("adding new roi from image '%s'", metadata)
                    center = rect.central()
                    comment = f"ROI for {model}, centered at P={center}, width={rect.width()}, height={rect.height()}"
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
                    return roi.roi_id
            except IntegrityError:
                log.warning("roi %s already exists", rect)
                sql = select(Roi.roi_id).where(Roi.x1 == rect.x1, Roi.y1 == rect.y1, Roi.x2 == rect.x2,Roi.y2 == rect.y2)
                with get_db_session() as session:
                    return session.scalars(sql).one()
