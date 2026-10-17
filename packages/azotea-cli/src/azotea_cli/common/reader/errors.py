# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# ----------------
# Own dependencies
# ----------------
from azotea_cli.common.errors import AzoteaError


class UnsupportedCFAError(AzoteaError):
    """Unsupported Color Filter Array type"""


class ReadMetadataError(AzoteaError):
    """Could not read EXIF metadata"""


class UnknownDateTimeFormatError(AzoteaError):
    """unknown observation date format string"""


class OutOfBoundsError(AzoteaError):
    """out of bounds rectangle"""


class MissingImageError(AzoteaError):
    """Image path does not exists"""


class MissingMandatorFitsError(AzoteaError):
    """Missing mandatory keywords in FITS image"""
