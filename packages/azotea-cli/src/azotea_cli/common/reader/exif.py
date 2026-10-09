import os
import logging
from datetime import datetime, timezone
from fractions import Fraction
from typing import Mapping, Any

import rawpy
import exifread

from azotea_cli.common.enums import HeaderType, ImageType, BayerPattern

from .interfaces import ImageReader, RawPixels
from .models import ImageMetadata
from .errors import ReadMetadataError, MissingDateObsError, UnknownDateTimeFormatError
####from ...provision import Provision, DefaultOptics


# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class ExifReader(ImageReader):

    def header_type(self) -> HeaderType:
        return HeaderType.EXIF

    def image_type(self) -> ImageType:
        return ImageType.LIGHT

    def handle_date_obs(self, exif: Mapping[str, Any], path: str) -> datetime:
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

    def handle_optics(self, exif: Mapping[str, Any]) -> tuple[float, float]:
        focal_len = exif.get("EXIF FocalLength")
        focal_len = float(Fraction(str(focal_len))) if focal_len is not None else 0
        f_number = exif.get("EXIF FNumber")
        f_number = round(float(Fraction(str(f_number))),1) if f_number is not None else 0
        if f_number == 0:
            prov = Provision()
            default = prov.load_default_optics()
            focal_len = default.focal_len
            f_number = default.f_number
        return (focal_len, f_number)

    def read_metadata(self, path: str) -> ImageMetadata:
        with open(path, "rb") as fd:
            exif = exifread.process_file(fd, details=True)
        if not exif:
            raise ReadMetadataError(f"{os.path.basename(path)}")
        make = exif.get("Image Make")
        make = str(make).strip() if make is not None else ""
        model = exif.get("Image Model")
        model = str(model).strip() if model is not None else None
        focal_len, f_number = self.handle_optics(exif)
        iso = exif.get("EXIF ISOSpeedRatings")
        iso = int(float(str(iso))) if iso is not None else None
        exptime = exif.get("EXIF ExposureTime")
        exptime = float(Fraction(str(exptime))) if exptime is not None else 0
        timestamp = self.handle_date_obs(exif, path)
        image_type=self.image_type()

        with rawpy.imread(path) as img:
             height, width = img.raw_image.shape
             black_levels = img.black_level_per_channel
             black_level = int(round(sum(black_levels)/len(black_levels),0))
             metadata = ImageMetadata(
                 width=width,
                 height=height,
                 make=make,
                 model=model,
                 exptime=exptime,
                 iso=iso,
                 gain= None,
                 black_level=black_level,
                 bayer=BayerPattern.RGGB,
                 imagetyp=image_type,
                 timestamp=timestamp,
                 focal_len=focal_len,
                 f_number=f_number,
             )
             log.info("METADATA = %s", metadata)
             return metadata


    def read_pixels(self, path:  str) -> RawPixels:
        """returns an object that implements the RawPixels interface"""
        ...
