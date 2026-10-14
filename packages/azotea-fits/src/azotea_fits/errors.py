from azotea_cli.common.errors import AzoteaError


class FitsError(AzoteaError):
    """Generic FITS error"""

    pass


class UnknownSoftwareCreatorError(FitsError):
    """Unknown FITS software creator"""
    pass
