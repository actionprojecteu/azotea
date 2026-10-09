import os

from .interface import ImageReader

FITS_EXTENSIONS = ('*.fit',  '*.fits', '*.fts')

def is_fits(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in FITS_EXTENSIONS

def get_reader(path: str) -> ImageReader:
    ...
