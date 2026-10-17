# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

# ----------------
# Own dependencies
# ----------------
from azotea_cli.common.types import ObjId

from .models import ObservationReport, SummaryRanged, SummaryTotals


class ReportsService(Protocol):
    """Meant to be exported to an external file (i.e CSV("""

    def get_all_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]: ...
    def get_ranged_data_by(
        self, observer_id: ObjId, since: datetime, until: datetime
    ) -> Sequence[ObservationReport]: ...
    def get_unpublished_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]: ...
    def get_latest_night_data_by(
        self, observer_id: ObjId
    ) -> tuple[Sequence[ObservationReport], datetime]: ...
    def get_latest_month_data_by(
        self, observer_id: ObjId
    ) -> tuple[Sequence[ObservationReport], datetime]: ...


class SummaryService(Protocol):
    """Meant to be displayed locally on console"""

    def totals_by(self, observer_id: ObjId) -> Sequence[SummaryTotals]: ...
    def ranged_summary(self) -> Sequence[SummaryRanged]: ...


class ExporterService(Protocol):
    def export(self, report_name: str, data: Sequence[ObservationReport]) -> None: ...
