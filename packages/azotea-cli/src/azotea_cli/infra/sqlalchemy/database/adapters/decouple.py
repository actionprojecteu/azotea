# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from collections.abc import Generator
from contextlib import contextmanager

import decouple
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------
# Own dependecies
# ---------------
from ..ports import Database

class DcplDatabase(Database):
    """main entry point instatinates this class"""

    def __init__(self, env_var: str = "DATABASE_URL") -> None:
        self._env_var = env_var

    def init(self) -> None:
        url: str = decouple.config(self._env_var)
        self._engine = create_engine(
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

__all__ = ["DcplDatabase"]
