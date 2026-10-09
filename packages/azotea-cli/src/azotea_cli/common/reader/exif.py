
from azotea_cli.common.enums import HeaderType

from .interfaces import ImageReader

class ExifReader(ImageReader):

    def header_type(self) -> HeaderType:
        return HeaderType.EXIF
