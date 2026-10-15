class FitsError(Exception):
    """FITS error"""

    pass


class UnknownSoftwareCreatorError(FitsError):
    """Unknown FITS software creator"""
    pass
