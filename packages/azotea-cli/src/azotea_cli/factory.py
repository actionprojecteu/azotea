import os

from .reader import ImageReader

FITS_EXTENSIONS = ('*.fit',  '*.fits', '*.fts')

def is_fits(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in FITS_EXTENSIONS

def reader_factory(path: str) -> ImageReader:
    ...
