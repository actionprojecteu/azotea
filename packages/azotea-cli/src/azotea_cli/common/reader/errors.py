from azotea_cli.common.errors import AzoteaError


class MissingCameraModelError(AzoteaError):
    """missing camera moedel from metadata"""

    pass


class UnsupportedCFAError(AzoteaError):
    """unsupported Color Filter Array type"""

    pass


class ReadMetadataError(AzoteaError):
    """could not read EXIF metadata"""

    pass


class MissingDateObsError(AzoteaError):
    """could not find date of observation in metadata"""

    pass


class UnknownDateTimeFormatError(AzoteaError):
    """unknown observation date format string"""

    pass


class OutOfBoundsError(AzoteaError):
    """out of bounds rectangle"""

    pass


class MissingImageError(AzoteaError):
    """Image path does not exists"""

    pass

class MissingMandatorFitsError(AzoteaError):
    """Missing mandatory keywords in FITS image"""
