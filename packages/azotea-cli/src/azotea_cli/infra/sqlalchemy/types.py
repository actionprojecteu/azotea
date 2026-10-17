# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from enum import StrEnum

# -----------------
# Enumeration types
# -----------------

class ValidState(StrEnum):
    CURRENT = "Current"
    EXPIRED = "Expired"
