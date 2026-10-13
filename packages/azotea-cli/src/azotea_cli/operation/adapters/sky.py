# ------------------
# standard libraries
# ------------------
#
import logging
import os
from collections.abc import Sequence

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from azotea_cli.common.models import ObjId

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Image, SkyBrightness, get_db_session

# from ..errors import
from ..interfaces import  SkyBrightnessRepo
from ..models import SkyStatsForm

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__.split(".")[-1])


class SqaSkyBrightnessRepo(SkyBrightnessRepo):
    def _translate(self, stats: SkyStatsForm) -> SkyBrightness:
        return SkyBrightness(
            image_id=stats.image_id,
            roi_id=stats.roi_id,
            aver_signal_R=stats.aver_signal_R,
            vari_signal_R=stats.vari_signal_R,
            aver_signal_G1=stats.aver_signal_G1,
            vari_signal_G1=stats.vari_signal_G1,
            aver_signal_G2=stats.aver_signal_G2,
            vari_signal_G2=stats.vari_signal_G2,
            aver_signal_B=stats.aver_signal_B,
            vari_signal_B=stats.vari_signal_B,
            published=False,
        )

    def _save_one_by_one(self, statistics: Sequence[SkyStatsForm]) -> None:
        for stats in statistics:
            try:
                with get_db_session() as session:
                    with session.begin():
                        session.add(self._translate(stats))
            except IntegrityError:
                log.warning(
                    "Skipping stats already present or violating a constraint: (image_id %s)",
                    stats.image_id,
                    exc_info=True,
                )

    def save_statistics(self, statistics: Sequence[SkyStatsForm]) -> None:
        with get_db_session() as session:
            try:
                with session.begin():
                    for stats in statistics:
                        session.add(self._translate(stats))
            except IntegrityError:
                log.warning(
                    "error saving a batch of %d statistics, looping one by one", len(statistics)
                )
                self._save_one_by_one(statistics)

    def pending_processing_by(self, observer_id: ObjId) -> Sequence[ObjId]:
        sql = select(Image.image_id).where(
            Image.observer_id == observer_id,
            ~select(SkyBrightness.image_id)
            .where(SkyBrightness.image_id == Image.image_id)
            .exists(),
        )
        with get_db_session() as session:
            image_ids = session.scalars(sql).all()
            return image_ids
