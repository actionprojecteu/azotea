
from azotea_cli.common.types import HeaderType

from ..ports import ImageReader

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

class FitsReader(ImageReader):

    def header_type(self) -> HeaderType:
        return HeaderType.FITS
