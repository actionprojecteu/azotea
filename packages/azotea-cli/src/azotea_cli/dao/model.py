# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


# --------------------
# System wide imports
# -------------------

from collections import OrderedDict
from typing import Optional, List, Type
from datetime import datetime, timezone

# ---------------------
# Third party libraries
# ---------------------

import pytz

from sqlalchemy import (
    Enum,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lica.sqlalchemy.noasync import Model

class Date(Model):
        __tablename__ = "date_t"

        # Date as YYYYMMDD integer
        date_id: Mapped[int] = mapped_column(primary_key=True)
        # Date as YYYY-MM-DD string
        sql_date: Mapped[str] = mapped_column(String(10))
        # Date as DD/MM/YYYY
        date: Mapped[str] = mapped_column(String(10))
        # Day of monty 1..31
        day: Mapped[int]
        # day of year 1..365
        day_year: Mapped[int]
        # Julian date at midnight
        julian_day: Mapped[float]
        # Sunday, Monday, Tuesday, ...
        weekday: Mapped[str] = mapped_column(String(9))
        # Sun, Mon, Tue, ...
        weekday_abbr: Mapped[str] = mapped_column(String(3))
        # 0=Sunday, 1=Monday
        weekday_num: Mapped[int]
        month_num: Mapped[int]
        # January, February, March, ...
        month: Mapped[str] = mapped_column(String(8))
        # Jan, Feb, Mar, ...
        month_abbr: Mapped[str] = mapped_column(String(3))
        year: Mapped[int]

class Time(Model):
        __tablename__ = "time_t"

        # HHMMSS as integer
        time_id: Mapped[int] = mapped_column(primary_key=True)
        # HH:MM:SS string
        time: Mapped[str] = mapped_column(String(8))
        hour: Mapped[int]
        minute: Mapped[int]
        second: Mapped[int]
        day_fraction: Mapped[float]
