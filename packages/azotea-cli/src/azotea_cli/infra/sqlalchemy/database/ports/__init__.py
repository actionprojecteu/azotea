# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------
from typing import  ContextManager, Protocol
from sqlalchemy.orm import Session

# ---------------------
# Third party libraries
# ---------------------


class Database(Protocol):
    """application software use this interface as the dependency"""

    def session(self) -> ContextManager[Session]: ...
