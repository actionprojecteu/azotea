class AzoteaFitsError(Exception):
    """FITS error"""

    pass


class UnknownSoftwareCreatorError(AzoteaFitsError):
    """Unknown FITS software creator"""

    pass


class MissingFitsFileError(AzoteaFitsError):
    """Unknown FITS software creator"""

    pass
