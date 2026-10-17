# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
from azotea_cli.common.errors import AzoteaError


class ConsentNotAgreedError(AzoteaError):
    """Consent form was not signed or was declined"""


class LocationMissingError(AzoteaError):
    """Location does not exists"""


class MissingDefaultLocationError(AzoteaError):
    """Default location is not set"""


class ObserverMissingError(AzoteaError):
    """Observer does not exists"""


class MissingDefaultObserverError(AzoteaError):
    """Default observer is not set"""


class CameraMissingError(AzoteaError):
    """Camera does not exists"""


class MissingDefaultCameraError(AzoteaError):
    """Default camera is not set"""


class RoiMissingError(AzoteaError):
    """Roi does not exists"""


class MissingDefaultRoiError(AzoteaError):
    """Default roi is not set"""


class FocalLenMissingError(AzoteaError):
    """Default focal length not set"""


class FNumberMissingError(AzoteaError):
    """Default f-number not set"""


class MissingCameraModelError(AzoteaError):
    """Missing camera model from metadata"""


class MissingExpTimeError(AzoteaError):
    """Missing exposure time from metadata"""


class MissingIsoOrGainError(AzoteaError):
    """Missing ISO or CMS gain from metadata"""


class MissingBlackLevelError(AzoteaError):
    """Missing black level from metadata"""


class MissingDateObsError(AzoteaError):
    """could not find date of observation in metadata"""
