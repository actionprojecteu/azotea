# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from collections import OrderedDict
from datetime import datetime, timezone
from typing import List, Optional, Type

# ---------------------
# Third party libraries
# ---------------------
import pytz
from lica.sqlalchemy.metadata import metadata
from lica.sqlalchemy.noasync.model import Model
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import ValidState, BayerPattern, HeaderType

DbValidState: Enum = Enum(
    ValidState,
    name="db_valid_state",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

DbBayerPattern: Enum = Enum(
    BayerPattern,
    name="db_bayer_pattern",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

DbHeaderType: Enum = Enum(
    HeaderType,
    name="db_header_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)


class Config(Model):
    __tablename__ = "config_t"

    section: Mapped[str] = mapped_column(String(32), primary_key=True)
    prop: Mapped[str] = mapped_column("property", String(255), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"Config(section={self.section!r}, prop={self.prop!r}, value={self.value!r})"


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


class Location(Model):
    __tablename__ = "location_t"

    location_id: Mapped[int] = mapped_column(primary_key=True)
    # Geographical longitude in decimal degrees
    longitude: Mapped[Optional[float]]
    # Geographical in decimal degrees
    latitude: Mapped[Optional[float]]
    # Descriptive name of this unitque location
    site_name: Mapped[str]
    # village, town, city, etc name
    location: Mapped[str]
    # randomized coordinates flag
    randomized: Mapped[Optional[bool]]
    # UTC offset, time zone as offset from UTC. i.e. GMT+1 = +1
    utc_offset: Mapped[Optional[float]]
    __table_args__ = (UniqueConstraint("site_name", "location"),)


class Observer(Model):
    __tablename__ = "observer_t"

    observer_id: Mapped[int] = mapped_column(primary_key=True)
    family_name: Mapped[str]
    surname: Mapped[str]
    affiliation: Mapped[Optional[str]]
    acronym: Mapped[Optional[str]]
    valid_since: Mapped[datetime]
    valid_until: Mapped[datetime]
    valid_state: Mapped[ValidState] = mapped_column(DbValidState)

    __table_args__ = (
        UniqueConstraint(
            "family_name", "surname", "affiliation", "acronym", "valid_since", "valid_until"
        ),
    )


class Camera(Model):
    __tablename__ = "camera_t"

    camera_id: Mapped[int] = mapped_column(primary_key=True)
    # Manuf + Camera Model (taken from EXIF data or FITS header)
    model: Mapped[str] = mapped_column(unique=True)
    # global bias (not per channel)
    bias: Mapped[int]
    # File extension produced by a camera (i.e. CR2, NEF)
    extension: Mapped[str]
    # Either 'EXIF' or 'FITS'
    header_type: Mapped[HeaderType] = mapped_column(DbHeaderType)
    # Either "RGGB", "BGGR", "GRBG" , "GBGR"
    bayer_pattern: Mapped[BayerPattern] =  mapped_column(DbBayerPattern)
    # Number of raw columns, without debayering
    width: Mapped[int]
    # Number of raw rows, without debayering
    height: Mapped[int]
    # pixel size in microns (width)
    x_pixsize: Mapped[Optional[float]]
    # pixel size in microns (height)
    y_pixsize: Mapped[Optional[float]]
