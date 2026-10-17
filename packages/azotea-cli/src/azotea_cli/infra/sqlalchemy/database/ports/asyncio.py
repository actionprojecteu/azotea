# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from typing import AsyncContextManager, Protocol

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncDatabase(Protocol):
    """application software use this interface as the dependency"""

    def session(self) -> AsyncContextManager[AsyncSession]: ...
