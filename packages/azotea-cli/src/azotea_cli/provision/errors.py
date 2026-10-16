from azotea_cli.common.errors import AzoteaError

# ------------------
# Package exceptions
# ------------------


class ConsentNotAgreedError(AzoteaError):
    """Consent form was not signed or was declined"""

    pass


class LocationMissingError(AzoteaError):
    """Location does not exists"""

    pass


class MissingDefaultLocationError(AzoteaError):
    """Default location is not set"""

    pass


class ObserverMissingError(AzoteaError):
    """Observer does not exists"""

    pass


class MissingDefaultObserverError(AzoteaError):
    """Default observer is not set"""

    pass


class CameraMissingError(AzoteaError):
    """Camera does not exists"""

    pass


class MissingDefaultCameraError(AzoteaError):
    """Default camera is not set"""

    pass


class RoiMissingError(AzoteaError):
    """Roi does not exists"""

    pass


class MissingDefaultRoiError(AzoteaError):
    """Default roi is not set"""

    pass


class FocalLenMissingError(AzoteaError):
    """default focal length not set"""

    pass


class FNumberMissingError(AzoteaError):
    """default f-number not set"""

    pass


class MissingCameraModelError(AzoteaError):
    """missing camera model from metadata"""

    pass


class MissingExpTimeError(AzoteaError):
    """missing exposure time from metadata"""

    pass


class MissingIsoOrGainError(AzoteaError):
    """Missing ISO or CMS GAIN from metadata"""

    pass


class MissingBlackLevelError(AzoteaError):
    """Missing ISO or CMS GAIN from metadata"""

    pass


class MissingDateObsError(AzoteaError):
    """could not find date of observation in metadata"""

    pass
