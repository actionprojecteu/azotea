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
from azotea_cli.reports.ports import SummaryService
from azotea_cli.reports.models import SummaryRanged, SummaryTotals

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class SqaSummaryService(SummaryService):
    def totals_by(self, observer_id: ObjId) -> Sequence[SummaryTotals]:
        raise NotImplementedError

    def ranged_summary_by(self, observer_id: ObjId) -> Sequence[SummaryRanged]:
        raise NotImplementedError
