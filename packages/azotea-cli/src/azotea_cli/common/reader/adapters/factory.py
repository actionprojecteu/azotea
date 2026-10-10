import os

from ..interfaces import ImageReader, ReaderFactory
from .exif import ExifReader
from .fits import FitsReader

FITS_EXTENSIONS = ('*.fit',  '*.fits', '*.fts')

def is_fits(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in FITS_EXTENSIONS

class ReaderFactoryImpl(ReaderFactory):
    def get_reader(self, path: str) -> ImageReader:
        if is_fits(path):
            return FitsReader()
        else:
            return ExifReader()
