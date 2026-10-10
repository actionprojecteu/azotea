# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from datetime import datetime

# ---------------------
# Third party libraries
# ---------------------

from lica.sqlalchemy.noasync.model import Model
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from azotea_cli.common.enums import BayerPattern, HeaderType, ImageType, ValidState
from .enums import DbBayerPattern, DbHeaderType, DbImageType, DbValidState


# ------
# Models
# ------
#
class Config(Model):
    __tablename__ = "config_t"

    section: Mapped[str] = mapped_column(String(32), primary_key=True)
    property: Mapped[str] = mapped_column("property", String(255), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"Config(section={self.section!r}, prop={self.property!r}, value={self.value!r})"


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
    longitude: Mapped[float | None]
    # Geographical in decimal degrees
    latitude: Mapped[float | None]
    # Descriptive name of this unitque location
    site_name: Mapped[str]
    # village, town, city, etc name
    location: Mapped[str]
    # randomized coordinates flag
    randomized: Mapped[bool | None]
    # UTC offset, time zone as offset from UTC. i.e. GMT+1 = +1
    utc_offset: Mapped[float | None]
    __table_args__ = (UniqueConstraint("site_name", "location"),)


class Observer(Model):
    __tablename__ = "observer_t"

    observer_id: Mapped[int] = mapped_column(primary_key=True)
    family_name: Mapped[str]
    surname: Mapped[str]
    affiliation: Mapped[str | None]
    acronym: Mapped[str | None]
    valid_since: Mapped[datetime] = mapped_column(DateTime)
    valid_until: Mapped[datetime]= mapped_column(DateTime)
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
    bayer_pattern: Mapped[BayerPattern] = mapped_column(DbBayerPattern)
    # Number of raw columns, without debayering
    width: Mapped[int]
    # Number of raw rows, without debayering
    height: Mapped[int]
    # pixel size in microns (width)
    x_pixsize: Mapped[float | None]
    # pixel size in microns (height)
    y_pixsize: Mapped[float | None]


class Roi(Model):
    __tablename__ = "roi_t"

    roi_id: Mapped[int] = mapped_column(primary_key=True)
    # x1 should be x1 <= x2
    x1: Mapped[int]
    # y1 should be y1 <= y2
    y1: Mapped[int]
    x2: Mapped[int]
    y2: Mapped[int]
    # as NumPy region text, ie. [y1:y2,x1:x2]
    display_name: Mapped[str]
    # Descriptive comment
    comment: Mapped[str | None]

    __table_args__ = (
        UniqueConstraint(
            "x1",
            "y1",
            "x2",
            "y2",
        ),
        UniqueConstraint(
            "display_name",
        ),
    )


class Image(Model):
    __tablename__ = "image_t"

    image_id: Mapped[int] = mapped_column(primary_key=True)
    # Image name without the parent path
    name: Mapped[str]
    # Original directory path
    directory: Mapped[str]
    # Image hash (alternative key in fact)
    hash: Mapped[bytes] = mapped_column(LargeBinary(256), unique=True)
    # DSLR ISO sensivity from EXIF
    iso: Mapped[int | None]
    # For imagers that do not have ISO (i.e CMOS astrocameras saving in FITS)
    gain: Mapped[float | None]
    # exposure time in seconds
    exptime: Mapped[float]
    # Either from image metadata or config default
    focal_length: Mapped[float | None]
    # Either from image metadata or config default
    f_number: Mapped[float | None]
    # Either BIAS, DARK, FLAT or LIGHT
    imagetype: Mapped[ImageType] = mapped_column(DbImageType)
    # false = image is ok, true = flagged as corrupt image
    flagged: Mapped[bool]
    # session identifier YYYYMMDDHHMMSS
    session: Mapped[int] = mapped_column(BigInteger)
    # Set of foreign keys
    date_id: Mapped[int] = mapped_column(ForeignKey("date_t.date_id"))
    time_id: Mapped[int] = mapped_column(ForeignKey("time_t.time_id"))
    camera_id: Mapped[int] = mapped_column(ForeignKey("camera_t.camera_id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("location_t.location_id"))
    observer_id: Mapped[int] = mapped_column(ForeignKey("observer_t.observer_id"))


class SkyBrightness(Model):
    __tablename__ = "sky_brightness_t"

    image_id: Mapped[int] =  mapped_column(ForeignKey("image_t.image_id"), primary_key=True)
    roi_id: Mapped[int] =  mapped_column(ForeignKey("roi_t.roi_id"), primary_key=True)

    # Sky Brightness measurements
    aver_signal_R: Mapped[float]
    vari_signal_R: Mapped[float]
    aver_signal_G1: Mapped[float]
    vari_signal_G1: Mapped[float]
    aver_signal_G2: Mapped[float]
    vari_signal_G2: Mapped[float]
    aver_signal_B: Mapped[float]
    vari_signal_B: Mapped[float]
    # published to server
    published: Mapped[bool]
