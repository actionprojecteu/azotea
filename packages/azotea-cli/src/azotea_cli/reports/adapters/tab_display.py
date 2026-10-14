# ------------------
# standard libraries
# ------------------

import logging
from collections.abc import Sequence
from datetime import datetime
from dataclasses import asdict

# ---------------------
# Third party libraries
# ---------------------
from tabulate import tabulate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from azotea_cli.common.models import ObjId

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import get_db_session
from azotea_cli.reports.ports import DisplayService
from azotea_cli.reports.models import SummaryRanged, SummaryTotals

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class TabDisplayService(DisplayService):
    def show_totals(self, data: Sequence[SummaryTotals]) -> None:
        print(tabulate(data, headers="keys", tablefmt="grid"))



    def show_ranged_summary(self, data: Sequence[SummaryRanged]) -> None:
        print(tabulate(data, headers="keys", tablefmt="grid"))
