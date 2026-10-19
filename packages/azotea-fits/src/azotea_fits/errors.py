# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
class AzoteaFitsError(Exception):
    """AzoteaFitsError"""

    def __str__(self):
        msg = self.__doc__
        return f"{msg}: {self.args[0]}." if self.args else f"{msg}."


class UnknownSoftwareCreatorError(AzoteaFitsError):
    """Unknown FITS software creator"""


class MissingFitsFileError(AzoteaFitsError):
    """Unknown FITS software creator"""


class ReadMetadataError(AzoteaFitsError):
    """Could not read image metadata"""
