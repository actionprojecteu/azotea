# ------------------
# standard libraries
# ------------------

import logging

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from azotea_cli.common.models import ObjId


# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Camera, get_db_session

from ..errors import (
    CameraMissingError,
    MissingDefaultCameraError,
)
from ..interfaces import ReportsService
from ..models import ObservationReport


# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------------------
# Create/Update location use case
# -------------------------------


class ReportsServiceImpl(ReportsService):
    pass
