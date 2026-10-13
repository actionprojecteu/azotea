# ------------------
# standard libraries
# ------------------

import logging
from collections.abc import Sequence
from datetime import datetime

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from azotea_cli.common.models import ObjId

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import get_db_session

from azotea_cli.reports.ports import ReportsService
from azotea_cli.reports.models import ObservationReport

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaReportsService(ReportsService):
    def get_all_data_by(self, observer_id: ObjId) -> Sequence[ObservationReport]:
        return list()

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
