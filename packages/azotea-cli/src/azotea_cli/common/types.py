# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from datetime import datetime, timezone

# For the time being ObjId is an alias
type ObjId = int

# =========
# Constants
# =========
FOREVER = datetime(2999, 12, 31, 23, 59, 00, tzinfo=timezone.utc)
