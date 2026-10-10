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
from azotea_cli.infra.sqlalchemy import Roi
from azotea_cli.common.rect import Rect, Point

from . import config, consent
from .errors import (
    ConsentNotAgreedError,
    FocalLenMissingError,
    FNumberMissingError,
    RoiExistsError,
)
from .models import RoiForm

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

engine, SessionFactory = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------------------
# Create/Update location use case
# -------------------------------


def create(form: RoiForm, as_default: bool) -> None:
    with SessionFactory() as session:
        rect = None
        try:
            with session.begin():
                consent.check_signed(session)
                log.info("adding new roi '%s'", form)
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
                if as_default:
                    session.flush()  # Ejecuta el INSERT y carga la PK en roi.id
                    config.save(session, "roi", "roi_id", str(roi.roi_id))
        except ConsentNotAgreedError:
            raise
        except IntegrityError:
            raise RoiExistsError(str(rect))


def create_from_image(path: str, width: int, height: int, as_default: bool) -> None:
    with SessionFactory() as session:
        rect = None
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
                log.info("adding new roi from image '%s'", path)
                reader = get_reader(path)
                _, extension = os.path.splitext(path)
                metadata = reader.read_metadata(path, def_focal_len, def_f_number)
                dim = Point(width, height) * 2 # to raw coordinates
                raw_size = Point(metadata.width, metadata.height)
                raw_screen = Rect.from_points(Point.zero(), raw_size)
                rect = Rect.from_points(Point.zero(), dim).recenter_on(raw_screen)
                rect = rect // 2 # to each plane coordinates
                model = metadata.model if metadata.model.startswith(metadata.make) else  f"{metadata.make} {metadata.model}"
                center = rect.central()
                comment = f"ROI for {model}, centered at P={center}, width={width}, height={height}"
                roi = Roi(
                   x1=rect.x1,
                   y1=rect.y1,
                   x2=rect.x2,
                   y2=rect.y2,
                   display_name=str(rect),
                   comment=comment,
               )
                session.add(roi)
        except ConsentNotAgreedError:
            raise
        except IntegrityError:
            raise RoiExistsError(str(rect))
