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
from azotea_cli.common.rect import Point, Rect

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Roi

from ..errors import (
    RoiExistsError,
    MissingDefaultRoiError
)
from ..interfaces import IRoiProv
from ..models import RoiCenteredForm, RoiForm, DefaultOptics
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


class RoiProvImpl(IRoiProv):

    def set_default(self, roi_id: int) -> None:
        with SessionFactory() as session:
            config.save(session, "roi", "roi_id", str(roi_id))

    def get_default(self) -> int:
        with SessionFactory() as session:
            roi_id = config.load(session, "roi", "roi_id")
            if roi_id is None:
                raise MissingDefaultRoiError
            return int(roi_id)

    def create(self, form: RoiForm, as_default: bool) -> int:
        with SessionFactory() as session:
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
                    roi_id = roi.roi_id
                    if as_default:
                        log.info("saving default roi_id: %d", roi_id)
                        config.save(session, "roi", "roi_id", str(roi.roi_id))
            except IntegrityError:
                raise RoiExistsError(str(rect))
        return roi_id

    def create_from_image(self, path: str, form: RoiCenteredForm, optics: DefaultOptics, as_default: bool) -> int:
        with SessionFactory() as session:
            rect = None
            try:
                with session.begin():
                    log.info("adding new roi from image '%s'", path)
                    reader = get_reader(path)
                    _, extension = os.path.splitext(path)
                    metadata = reader.read_metadata(path, optics.focal_len, optics.f_number)
                    dim = Point(form.width, form.height) * 2  # to raw coordinates
                    raw_size = Point(metadata.width, metadata.height)
                    raw_screen = Rect.from_points(Point.zero(), raw_size)
                    rect = Rect.from_points(Point.zero(), dim).recenter_on(raw_screen)
                    rect = rect // 2  # to each plane coordinates
                    model = (
                        metadata.model
                        if metadata.model.startswith(metadata.make)
                        else f"{metadata.make} {metadata.model}"
                    )
                    center = rect.central()
                    comment = (
                        f"ROI for {model}, centered at P={center}, width={form.width}, height={form.height}"
                    )
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
                    roi_id = roi.roi_id
                    if as_default:
                        log.info("saving default roi_id: %d", roi_id)
                        config.save(session, "roi", "roi_id", str(roi.roi_id))

            except IntegrityError:
                raise RoiExistsError(str(rect))
        return roi_id
