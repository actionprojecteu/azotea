# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import decouple
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ...ports.asyncio import AsyncDatabase


class AsyncDcplDatabase(AsyncDatabase):
    """main entry point instatinates this class"""

    def __init__(self, env_var: str = "DATABASE_URL") -> None:
        self._env_var = env_var

    def init(self) -> None:
        url: str = decouple.config(self._env_var)
        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = async_sessionmaker(
            self._engine, autoflush=False, expire_on_commit=False
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_factory() as _session:
            yield _session

    @property
    def engine(self) -> AsyncEngine:
        return self._engine




__all__ = ["DcplDatabase", "AsyncDcplDatabase"]
