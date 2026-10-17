# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from typing import ContextManager, Protocol

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy.orm import Session


class Database(Protocol):
    """application software use this interface as the dependency"""

    def session(self) -> ContextManager[Session]: ...
