import logging
from collections.abc import MutableSequence, Sequence
from datetime import datetime
from typing import Any

from astropy.io.fits import Header
from azotea_cli.common.reader.adapters.fits import (
    APTDIA,
    BAYERPAT,
    COMMENT,
    DATE_OBS,
    EXPTIME,
    FOCALLEN,
    HISTORY,
    IMAGETYP,
    INSTRUME,
    LOG_GAIN,
    NAXIS1,
    NAXIS2,
    PEDESTAL,
    XPIXSIZE,
    YPIXSIZE,
)
from azotea_cli.common.types import BayerPattern, ImageType

from .generic import GenericMetadataFix, GenericMetadataInsert

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

class SharpCapMetadataFix(GenericMetadataFix):
    pass

class SharpCapMetadataInsert(GenericMetadataInsert):
    pass
