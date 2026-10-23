# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from datetime import datetime, timezone
from typing import NamedTuple


class ObjId(NamedTuple):
    """Object Id as a new type"""
    id: int

# =========
# Constants
# =========
FOREVER = datetime(2999, 12, 31, 23, 59, 00, tzinfo=timezone.utc)
