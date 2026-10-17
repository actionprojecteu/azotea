# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------

import logging
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# ---------------
# Own dependecies
# ---------------
from azotea_cli import __version__
from azotea_cli.common.types import ObjId
from azotea_cli.infra.sqlalchemy import (
    Camera,
    Database,
    Date,
    Image,
    Location,
    Observer,
    Roi,
    SkyBrightness,
    Time,
)
from azotea_cli.reports.models import ObservationReport
from azotea_cli.reports.ports import ReportsService

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaReportsService(ReportsService):
    def __init__(self, db: Database) -> None:
        self.db = db

    def _get_observer_date_range(
        self, session: Session, observer_id: ObjId
    ) -> tuple[int | None, int | None]:
        query = select(func.min(Image.date_id), func.max(Image.date_id)).where(
            Image.observer_id == observer_id
        )
        return session.execute(query).one()

    def _report_selector(self, observer_id) -> Any:
        return (
            select(
                Image.session.label("session"),
                Observer.family_name.label("family_name"),
                Observer.surname.label("surname"),
                Observer.acronym.label("acronym"),
                Location.site_name.label("site_name"),
                Location.location.label("location"),
                Image.imagetype.label("image_type"),
                Date.sql_date.label("date"),
                Time.time.label("time"),
                Image.name.label("image_name"),
                Camera.model.label("model"),
                Image.iso.label("iso"),
                Image.gain.label("gain"),
                Roi.display_name.label("display_name"),
                Image.exptime.label("exptime"),
                SkyBrightness.aver_signal_R.label("aver_R"),
                SkyBrightness.vari_signal_R.label("vari_R"),
                SkyBrightness.aver_signal_G1.label("aver_G1"),
                SkyBrightness.vari_signal_G1.label("vari_G1"),
                SkyBrightness.aver_signal_G2.label("aver_G2"),
                SkyBrightness.vari_signal_G2.label("vari_G2"),
                SkyBrightness.aver_signal_B.label("aver_B"),
                SkyBrightness.vari_signal_B.label("vari_B"),
                Camera.bias.label("bias"),
            )
            .select_from(Image)
            .join(SkyBrightness, SkyBrightness.image_id == Image.image_id)
            .join(Date, Date.date_id == Image.date_id)
            .join(Time, Time.time_id == Image.time_id)
            .join(Camera, Camera.camera_id == Image.camera_id)
            .join(Location, Location.location_id == Image.location_id)
            .join(Observer, Observer.observer_id == Image.observer_id)
            .join(Roi, Roi.roi_id == SkyBrightness.roi_id)
            .where(Image.observer_id == observer_id)
        )

    def _to_all(self, x: Mapping[str, Any]) -> ObservationReport:
        return ObservationReport(
            version=__version__,
            session=x["session"],
            observer=f"{x['family_name']} {x['surname']}",
            affiliation=x["acronym"],
            site_name=x["site_name"],
            location=x["location"],
            image_type=x["image_type"],
            date_obs=datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M:%S"),
            image_name=x["image_name"],
            camera_model=x["model"],
            iso=x["iso"],
            gain=x["gain"],
            roi=x["display_name"],
            exptime=x["exptime"],
            bias=x["bias"],
            aver_signal_R=x["aver_R"],
            vari_signal_R=x["vari_R"],
            aver_signal_G1=x["aver_G1"],
            vari_signal_G1=x["vari_G1"],
            aver_signal_G2=x["aver_G2"],
            vari_signal_G2=x["vari_G2"],
            aver_signal_B=x["aver_B"],
            vari_signal_B=x["vari_B"],
        )

    def get_all_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        query = self._report_selector(observer_id)
        with self.db.session() as session:
            rows = session.execute(query).mappings()
            return [self._to_all(dict(row)) for row in rows]

    def get_ranged_data_by(
        self, observer_id: ObjId, since: datetime, until: datetime
    ) -> Sequence[ObservationReport]:
        max_date_id = int(until.strftime("%Y%m%d%H%M%S"))
        min_date_id = int(since.strftime("%Y%m%d%H%M%S"))
        query = (
            self._report_selector(observer_id)
            .where(Image.date_id.between(min_date_id, max_date_id))
            .order_by(Image.date_id.desc(), Image.time_id.desc())
        )
        with self.db.session() as session:
            rows = session.execute(query).mappings()
            return [self._to_all(dict(row)) for row in rows]

    def get_unpublished_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        query = (
            self._report_selector(observer_id)
            .where(SkyBrightness.published == False)  # noqa: E712
            .order_by(Image.date_id.desc(), Image.time_id.desc())
        )
        with self.db.session() as session:
            rows = session.execute(query).mappings()
            return [self._to_all(dict(row)) for row in rows]

    def get_latest_night_data_by(
        self, observer_id: ObjId
    ) -> tuple[Sequence[ObservationReport], datetime]:
        with self.db.session() as session:
            _, max_date_id = self._get_observer_date_range(session, observer_id)
            if max_date_id is None:
                raise RuntimeError("This should not happen (max_date_id)")
            max_year = max_date_id // 10000
            max_month = (max_date_id % 10000) // 100
            max_day = max_date_id % 100
            query = (
                self._report_selector(observer_id)
                .where(Image.date_id == max_date_id)
                .order_by(Image.date_id.desc(), Image.time_id.desc())
            )
            rows = session.execute(query).mappings()
            max_date = datetime(year=max_year, month=max_month, day=max_day)
            return [self._to_all(dict(row)) for row in rows], max_date

    def get_latest_month_data_by(
        self, observer_id: ObjId
    ) -> tuple[Sequence[ObservationReport], datetime]:
        with self.db.session() as session:
            _, max_date_id = self._get_observer_date_range(session, observer_id)
            if max_date_id is None:
                raise RuntimeError("This should not happen (max_date_id)")
            max_year = max_date_id // 10000
            max_month = (max_date_id % 10000) // 100
            query = (
                self._report_selector(observer_id)
                .where(Date.year == max_year)
                .where(Date.month_num == max_month)
                .order_by(Image.date_id.desc(), Image.time_id.desc())
            )
            rows = session.execute(query).mappings()
            max_date = datetime(year=max_year, month=max_month, day=1)
            return [self._to_all(dict(row)) for row in rows], max_date
