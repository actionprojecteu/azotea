# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from contextlib import contextmanager
from collections.abc import Generator
# ---------------------
# Third party libraries
# ---------------------
#
import decouple
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

# get the module logger
log = logging.getLogger(__name__.split(".")[-1])

url: str = decouple.config("DATABASE_URL")
engine: Engine = create_engine(url, pool_pre_ping=True, connect_args={"check_same_thread": False})
_SessionFactory = sessionmaker(engine, autoflush=False, expire_on_commit=False)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def sqa_logging(debug: bool) -> None:
    if debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        # This is needed, otherwise aiosqlite msgs will jump in
        logging.getLogger("aiosqlite").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


__all__ = ["engine", "get_db_session", "sqa_logging"]
