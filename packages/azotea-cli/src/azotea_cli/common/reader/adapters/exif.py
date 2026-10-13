import logging
import os
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Mapping

import exifread
import numpy as np
import rawpy
from rawpy._rawpy import RawPy

from azotea_cli.common.models import BayerIndex, BayerPattern, HeaderType
from azotea_cli.common.rect import Point, Rect

from ..errors import (
    MissingImageError,
    MissingCameraModelError,
    MissingDateObsError,
    OutOfBoundsError,
    ReadMetadataError,
    UnknownDateTimeFormatError,
    UnsupportedCFAError,
)
from ..interfaces import ImageReader, RawPixels
from ..models import ImageMetadata, IntArray2D
from ..utils import image_type_by_path

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


def to_positive_float(value: Any, default: float) -> float:
    if value in (None, 0, "0"):
        return default
    try:
        result = round(float(Fraction(str(value))), 2)
    except (ValueError, ZeroDivisionError, TypeError):
        return default
    return result if result > 0 else default


def handle_date_obs(exif: Mapping[str, Any], path: str) -> datetime:
    date_obs = None
    for key in ("Image DateTime", "EXIF DateTimeOriginal"):
        date_obs = exif.get(key)
        if date_obs:
            date_obs = str(date_obs)
            break
    if date_obs is None:
        raise MissingDateObsError(os.path.basename(path))
    new_date_obs = None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            new_date_obs = datetime.strptime(date_obs, fmt)
        except Exception:
            pass
        else:
            break
    if new_date_obs is None:
        raise UnknownDateTimeFormatError(date_obs)
    return new_date_obs.replace(tzinfo=timezone.utc)


class ExifReader(ImageReader):
    def header_type(self) -> HeaderType:
        return HeaderType.EXIF

    def handle_optics(
        self, exif: Mapping[str, Any], def_focal_len: float, def_f_number: float
    ) -> tuple[float, float]:
        focal_len = to_positive_float(exif.get("EXIF FocalLength"), def_focal_len)
        f_number = exif.get("EXIF FNumber")
        f_number = to_positive_float(exif.get("EXIF FNumber"), def_f_number)
        return (focal_len, f_number)

    def read_metadata(self, path: str, def_focal_len: float, def_f_number: float) -> ImageMetadata:
        with open(path, "rb") as fd:
            exif = exifread.process_file(fd, details=True)
        if not exif:
            raise ReadMetadataError(f"{os.path.basename(path)}")
        make = exif.get("Image Make")
        make = str(make).strip() if make is not None else ""
        model = exif.get("Image Model")
        model = str(model).strip() if model is not None else None
        if model is None:
            raise MissingCameraModelError(f"{os.path.basename(path)}")
        focal_len, f_number = self.handle_optics(exif, def_focal_len, def_f_number)
        iso = exif.get("EXIF ISOSpeedRatings")
        iso = int(float(str(iso))) if iso is not None else None
        exptime = exif.get("EXIF ExposureTime")
        exptime = float(Fraction(str(exptime))) if exptime is not None else 0
        timestamp = handle_date_obs(exif, path)
        image_type = image_type_by_path(path)
        with rawpy.imread(path) as img:
            height, width = img.raw_image.shape
            black_levels = img.black_level_per_channel
            black_level = int(round(sum(black_levels) / len(black_levels), 0))  # mean black level
            color_desc = img.color_desc.decode("utf-8")
            if color_desc != "RGBG":
                raise UnsupportedCFAError(color_desc)
            cfa = "".join(
                map(
                    lambda c: {"Gr": "G", "Gb": "G"}.get(c, c),
                    [BayerIndex(i).name for i in img.raw_pattern.ravel()],
                )
            )
            bayer = BayerPattern(cfa)
            header_type = self.header_type()
            _, extension = os.path.splitext(path)

        metadata = ImageMetadata(
            width=width,
            height=height,
            make=make,
            model=model,
            exptime=exptime,
            iso=iso,
            gain=None,
            black_level=black_level,
            bayer=bayer,
            imagetyp=image_type,
            timestamp=timestamp,
            focal_len=focal_len,
            f_number=f_number,
            header_type=header_type,
            extension=extension,
        )
        return metadata

    def read_pixels(self, path: str) -> RawPixels:
        """returns an object that implements the RawPixels interface"""
        if not os.path.isfile(path):
            raise  MissingImageError(path)
        raw = rawpy.imread(path)
        return ExifRawPixels(raw)


class ExifRawPixels:
    def __init__(self, raw: RawPy) -> None:
        self.img = raw
        self.black_levels = raw.black_level_per_channel
        self.shape = raw.raw_image.shape
        self.pattern = raw.raw_pattern

    # No context managers here, we need to keep the internal numpy
    # raw_pixels array alive while statistics are being computed
    def __del__(self) -> None:
        try:
            if self.img is not None:
                self.black_levels = None
                self.shape = None
                self.img.close()
        finally:
            self.img = None

    def _section(
        self,
        x: int,
        y: int,
        section: Rect | None,
    ) -> IntArray2D:
        screen = Rect.from_points(Point.zero(), Point(x=self.shape[1], y=self.shape[0])) // 2
        if section is None:
            section = screen
        elif not screen.contains(section):
            raise OutOfBoundsError(section)
        section = section * 2
        x1 = x + section.x1
        y1 = y + section.y1
        x2 = section.x2
        y2 = section.y2
        return self.img.raw_image[y1:y2:2, x1:x2:2]

    def r(self, section: Rect | None) -> IntArray2D:
        y, x = np.argwhere(self.pattern == BayerIndex.R)[0]
        return self._section(x, y, section)

    def gr(self, section: Rect | None) -> IntArray2D:
        y, x = np.argwhere(self.pattern == BayerIndex.Gr)[0]
        return self._section(x, y, section)

    def gb(self, section: Rect | None) -> IntArray2D:
        y, x = np.argwhere(self.pattern == BayerIndex.Gb)[0]
        return self._section(x, y, section)

    def b(self, section: Rect | None) -> IntArray2D:
        y, x = np.argwhere(self.pattern == BayerIndex.B)[0]
        return self._section(x, y, section)

    def r_black(self) -> int:
        return self.black_levels[BayerIndex.R]

    def gr_black(self) -> int:
        return self.black_levels[BayerIndex.Gr]

    def gb_black(self) -> int:
        return self.black_levels[BayerIndex.Gb]

    def b_black(self) -> int:
        return self.black_levels[BayerIndex.B]
