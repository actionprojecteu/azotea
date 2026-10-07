from enum import StrEnum

class ValidState(StrEnum):
    CURRENT = "Current"
    EXPIRED = "Expired"

class HeaderType(StrEnum):
    FITS = "Fits"
    EXIF = "Exif"

class BayerPattern(StrEnum):
    RGGB = "RGGB"
    BGGR = "BGGR"
    GRBG = "GRBG"
    GBGR = "GBGR"

class ImageType(StrEnum):
    BIAS = "BIAS"
    DARK = "DARK"
    FLAT = "FLAT"
    LIGHT = "LIGHT"
