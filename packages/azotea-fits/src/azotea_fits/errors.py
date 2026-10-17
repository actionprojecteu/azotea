# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
class AzoteaFitsError(Exception):
    """FITS error"""

    pass


class UnknownSoftwareCreatorError(AzoteaFitsError):
    """Unknown FITS software creator"""

    pass


class MissingFitsFileError(AzoteaFitsError):
    """Unknown FITS software creator"""

    pass
