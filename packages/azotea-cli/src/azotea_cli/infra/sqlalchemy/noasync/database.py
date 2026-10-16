# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import ContextManager, Protocol

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


class Database(Protocol):
    """application software use this interface as the dependency"""

    def session(self) -> ContextManager[Session]: ...


class DatabaseByEnvVar(Database):
    """main entry point instatinates this class"""

    def __init__(self, env_var: str = "DATABASE_URL") -> None:
        self._env_var = env_var

    def init(self) -> None:
        url = decouple.config(self._env_var)
        self._engine: Engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(self._engine, autoflush=False, expire_on_commit=False)

    @contextmanager
    def session(self) -> Generator[Session]:
        with self._session_factory() as _session:
            yield _session

    @property
    def engine(self) -> Engine:
        return self._engine


def sqa_logging(debug: bool) -> None:
    if debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        # This is needed, otherwise aiosqlite msgs will jump in
        logging.getLogger("aiosqlite").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


__all__ = ["Database", "DatabaseByEnvVar", "sqa_logging"]
