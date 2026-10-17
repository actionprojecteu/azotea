# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import csv
import logging
import os
from collections.abc import Sequence
from dataclasses import asdict

# ---------------
# Own dependecies
# ---------------
from azotea_cli.reports.models import ObservationReport
from azotea_cli.reports.ports import ExporterService

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
