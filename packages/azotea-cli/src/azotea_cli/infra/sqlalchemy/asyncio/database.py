# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# ---------------------
# Third party libraries
# ---------------------
#
import decouple
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

# get the module logger
log = logging.getLogger(__name__.split(".")[-1])

url: str = decouple.config("DATABASE_URL")
engine: AsyncEngine = create_async_engine(url, pool_pre_ping=True, connect_args={"check_same_thread": False})
AsyncSessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session

def sqa_logging(debug: bool) -> None:
    if debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        # This is needed, otherwise aiosqlite msgs will jump in
        logging.getLogger("aiosqlite").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


__all__ = ["engine", "get_db_session", "sqa_logging"]
