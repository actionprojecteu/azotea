
from azotea_cli.common.models import HeaderType

from ..interfaces import ImageReader

class FitsReader(ImageReader):

    def header_type(self) -> HeaderType:
        return HeaderType.FITS
