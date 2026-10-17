# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import os
from datetime import datetime, timezone

# ---------------------
# Third party libraries
# ---------------------
from astropy.io import fits
from astropy.io.fits import HDUList

# ----------------
# Own dependencies
# ----------------
from azotea_cli.common.rect import Point, Rect
from azotea_cli.common.types import BayerIndex, BayerPattern, HeaderType

from ..errors import (
    MissingImageError,
    MissingMandatorFitsError,
    OutOfBoundsError,
    UnknownDateTimeFormatError,
)
from ..models import ImageMetadata, IntArray2D
from ..ports import ImageReader, RawPixels

# FITS relevant keywords
NAXIS1: str = "NAXIS1"
NAXIS2: str = "NAXIS2"
HISTORY: str = "HISTORY"
COMMENT: str = "COMMENT"
INSTRUME: str = "INSTRUME"
LOG_GAIN: str = "LOG-GAIN"
BAYERPAT: str = "BAYERPAT"
PEDESTAL: str = "PEDESTAL"
XPIXSIZE: str = "XPIXSZ"
YPIXSIZE: str = "YPIXSZ"
IMAGETYP: str = "IMAGETYP"
FOCALLEN: str = "FOCALLEN"
APTDIA: str = "APTDIA"
EXPTIME: str = "EXPTIME"
DATE_OBS: str = "DATE-OBS"


def bayer_layout(pattern: BayerPattern) -> list[tuple[int, int]]:
    """
    Turns a Bayyer pattern string into a 2x2 Bayer Matrix with the (row, column)
    coordinates of R, Gr, B y Gb.
    The matrix is given as a list, indexed by BayerIndex
    """
    coords = [(0, 0), (0, 0), (0, 0), (0, 0)]
    p = pattern.value
    # Patrón en orden fila-major:
    #   p[0] p[1]
    #   p[2] p[3]
    raw = [
        [p[0], p[1]],
        [p[2], p[3]],
    ]
    r_coords = next(
        (r, c) for r, row in enumerate(raw) for c, value in enumerate(row) if value == "R"
    )
    b_coords = next(
        (r, c) for r, row in enumerate(raw) for c, value in enumerate(row) if value == "B"
    )
    # El otro G de la fila de R es Gr.
    gr_coords = (r_coords[0], 1 - r_coords[1])
    # El otro G de la fila de B es Gb.
    gb_coords = (b_coords[0], 1 - b_coords[1])
    coords[BayerIndex.R] = r_coords
    coords[BayerIndex.Gr] = gr_coords
    coords[BayerIndex.B] = b_coords
    coords[BayerIndex.Gb] = gb_coords
    return coords


class FitsReader(ImageReader):
    MANDATORY_KEYWORDS = {
        NAXIS1,
        NAXIS2,
        BAYERPAT,
    }

    def header_type(self) -> HeaderType:
        return HeaderType.FITS

    def handle_date_obs(self, date_obs: str) -> datetime:
        new_date_obs = None
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S:%:z",
            "%Y-%m-%dT%H:%M:%S%Z",
            "%Y-%m-%dT%H:%M:%S.%f%:z",
            "%Y-%m-%dT%H:%M:%S.%f%Z",
        ):
            try:
                new_date_obs = datetime.strptime(date_obs, fmt)
            except Exception:
                pass
            else:
                break
        if new_date_obs is None:
            raise UnknownDateTimeFormatError(date_obs)
        return new_date_obs.replace(tzinfo=timezone.utc)

    def read_metadata(self, path: str) -> ImageMetadata:
        """returns an instance of ImageMetadata dataclass"""
        with fits.open(path) as hdul:
            header = hdul[0].header
            available = set(header.keys())
            if not self.MANDATORY_KEYWORDS < available:
                raise MissingMandatorFitsError(self.MANDATORY_KEYWORDS - available)
            width = header[NAXIS1]
            height = header[NAXIS2]
            make = None
            model = header.get(INSTRUME)
            exptime = header.get(EXPTIME)
            gain = header.get(LOG_GAIN)
            black_level = header.get(PEDESTAL)
            bayer = header[BAYERPAT]
            image_type = header.get(IMAGETYP)
            timestamp = self.handle_date_obs(header.get(DATE_OBS))
            focal_len = header.get(FOCALLEN)
            f_number = (
                None
                if header.get(APTDIA) is None or focal_len is None
                else round(focal_len / header[APTDIA], 2)
            )
            header_type = self.header_type()
            extension = os.path.splitext(path)[1]
            metadata = ImageMetadata(
                width=width,
                height=height,
                make=make,
                model=model,
                exptime=exptime,
                iso=None,
                gain=gain,
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
            raise MissingImageError(path)
        hdul = fits.open(path)
        return FitsRawPixels(hdul)


class FitsRawPixels:
    def __init__(self, hdul: HDUList) -> None:
        self.hdul = hdul
        header = hdul[0].header
        self.black_levels = [header.get(PEDESTAL)] * 4
        self.shape = (header[NAXIS2], header[NAXIS1])
        pattern = BayerPattern(header[BAYERPAT])
        self.coords = bayer_layout(pattern)

    def __del__(self) -> None:
        try:
            if self.hdul is not None:
                self.black_levels = None
                self.shape = None
                self.hdul.close()
        finally:
            self.hdul = None

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
        img: IntArray2D = self.hdul[0].data
        return img[y1:y2:2, x1:x2:2]

    def r(self, section: Rect | None) -> IntArray2D:
        y, x = self.coords[BayerIndex.R]
        return self._section(x, y, section)

    def gr(self, section: Rect | None) -> IntArray2D:
        y, x = self.coords[BayerIndex.Gr]
        return self._section(x, y, section)

    def gb(self, section: Rect | None) -> IntArray2D:
        y, x = self.coords[BayerIndex.Gb]
        return self._section(x, y, section)

    def b(self, section: Rect | None) -> IntArray2D:
        y, x = self.coords[BayerIndex.B]
        return self._section(x, y, section)

    def r_black(self) -> int:
        return self.black_levels[BayerIndex.R]

    def gr_black(self) -> int:
        return self.black_levels[BayerIndex.Gr]

    def gb_black(self) -> int:
        return self.black_levels[BayerIndex.Gb]

    def b_black(self) -> int:
        return self.black_levels[BayerIndex.B]
