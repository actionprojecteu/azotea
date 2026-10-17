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
from typing import Any

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import func, select
from lica_sqa import Database

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.types import ObjId
from azotea_cli.infra.sqlalchemy import (
    Date,
    Image,
    Observer,
    Roi,
    SkyBrightness,
)
from azotea_cli.reports.models import SummaryRanged, SummaryTotals
from azotea_cli.reports.ports import SummaryService

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaSummaryService(SummaryService):
    def __init__(self, db: Database) -> None:
        self.db = db

    def _report_selector_totals(self, observer_id) -> Any:
        return (
            select(
                Observer.family_name.label("family_name"),
                Observer.surname.label("surname"),
                Image.imagetype.label("image_type"),
                Image.flagged.label("flagged"),
                func.count("*").label("totals"),
            )
            .select_from(Image)
            .join(Observer, Observer.observer_id == Image.observer_id)
            .where(Image.observer_id == observer_id)
            .group_by(Observer.observer_id, Image.imagetype, Image.flagged)
            .order_by(Observer.observer_id, "totals")
        )

    def _report_selector_totals2(self) -> Any:
        return (
            select(
                Observer.family_name.label("family_name"),
                Observer.surname.label("surname"),
                Roi.display_name.label("display_name"),
                func.max(Roi.x2 - Roi.x1).label("width"),
                func.max(Roi.y2 - Roi.y1).label("height"),
                SkyBrightness.published.label("published"),
                func.count(SkyBrightness.published).label("total_published"),
            )
            .select_from(Image)
            .join(SkyBrightness, SkyBrightness.image_id == Image.image_id)
            .join(Observer, Observer.observer_id == Image.observer_id)
            .join(Date, Date.date_id == Image.date_id)
            .join(Roi, Roi.roi_id == SkyBrightness.roi_id)
            .group_by(Observer.observer_id, Roi.display_name, SkyBrightness.published)
            .order_by("total_published")
        )

    def _to_all_totals(self, x: Mapping[str, Any]) -> SummaryTotals:
        return SummaryTotals(
            observer=f"{x['family_name']} {x['surname']}",
            image_type=x["image_type"],
            flagged=x["flagged"],
            count=x["totals"],
        )

    def _to_all_totals2(self, x: Mapping[str, Any]) -> SummaryRanged:
        return SummaryRanged(
            observer=f"{x['family_name']} {x['surname']}",
            roi=x["display_name"],
            width=x["width"],
            height=x["height"],
            published=x["published"],
            count=x["total_published"],
        )

    def totals_by(self, observer_id: ObjId) -> Sequence[SummaryTotals]:
        query = self._report_selector_totals(observer_id)
        with self.db.session() as session:
            rows = session.execute(query).mappings()
            return [self._to_all_totals(dict(row)) for row in rows]

    def ranged_summary(self) -> Sequence[SummaryRanged]:
        query = self._report_selector_totals2()
        with self.db.session() as session:
            rows = session.execute(query).mappings()
            return [self._to_all_totals2(dict(row)) for row in rows]
