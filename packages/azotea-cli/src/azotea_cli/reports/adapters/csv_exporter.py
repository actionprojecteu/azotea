# ------------------
# standard libraries
# ------------------

import logging
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
from azotea_cli.infra.sqlalchemy import get_db_session

from azotea_cli.reports.ports import ExporterService
from azotea_cli.reports.models import ObservationReport

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class CsvExporterService(ExporterService):
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def export(self, data: Sequence[ObservationReport]) -> None:
        raise NotImplementedError
