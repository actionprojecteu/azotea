# ------------------
# standard libraries
# ------------------

import os
import logging
from collections.abc import Sequence
import csv
from dataclasses import asdict

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

    def export(self, report_name: str, data: Sequence[ObservationReport]) -> None:
        header = asdict(data[0]).keys()
        path = os.path.join(self.output_dir, f"{report_name}.csv")
        with open(path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=header)
            writer.writeheader()
            for row in data:
                writer.writerow(asdict(row))
