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
