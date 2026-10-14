# ------------------
# standard libraries
# ------------------

import logging
from collections.abc import Sequence, Mapping
from datetime import datetime
from typing import Any

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli import __version__
from azotea_cli.common.models import ObjId
from azotea_cli.infra.sqlalchemy import (
    Camera,
    Date,
    Image,
    Location,
    Observer,
    Roi,
    SkyBrightness,
    Time,
    get_db_session,
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
    def to_all(self, x: Mapping[str, Any]) -> ObservationReport:
        return ObservationReport(
            version=__version__,
            session=x["session"],
            observer=f"{x['family_name']} {x['surname']}",
            acronym=x["acronym"],
            site_name=x["site_name"],
            location=x["location"],
            imagetype=x["imagetype"],
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
            aver_signal_G1=x["aver_R"],
            vari_signal_G1=x["vari_R"],
            aver_signal_G2=x["aver_R"],
            vari_signal_G2=x["vari_R"],
            aver_signal_B=x["aver_R"],
            vari_signal_B=x["vari_R"],
        )

    def get_all_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        query = (
            select(
                Image.session.label("session"),
                Observer.family_name.label("family_name"),
                Observer.surname.label("surname"),
                Observer.acronym.label("acronym"),
                Location.site_name.label("site_name"),
                Location.location.label("location"),
                Image.imagetype.label("imagetype"),
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
                SkyBrightness.aver_signal_G1.label("aver_g1"),
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
            .order_by(Image.date_id.desc(), Image.time_id.desc())
        )
        with get_db_session() as session:
            result = session.execute(query).mappings()
            return list(map(self.to_all, result))


    def get_ranged_data_by(
        self, observer_id: ObjId, since: datetime, until: datetime
    ) -> Sequence[ObservationReport]:
        raise NotImplementedError

    def get_unpublished_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        raise NotImplementedError

    def get_latest_night_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        raise NotImplementedError

    def get_latest_month_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        raise NotImplementedError
