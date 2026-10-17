# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import os

# ----------------
# Own dependencies
# ----------------
from ..ports import ImageReader, ImageReaderFactory
from .exif import ExifReader
from .fits import FitsReader

FITS_EXTENSIONS = ('.fit',  '.fits', '.fts')

def is_fits(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in FITS_EXTENSIONS

class ImageReaderFactoryImpl(ImageReaderFactory):
    def get_reader(self, path: str) -> ImageReader:
        if is_fits(path):
            return FitsReader()
        else:
            return ExifReader()
