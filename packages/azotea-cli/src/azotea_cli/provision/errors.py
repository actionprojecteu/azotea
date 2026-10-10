from azotea_cli.common.errors import AzoteaError

# ------------------
# Package exceptions
# ------------------

class ConsentNotAgreedError(AzoteaError):
    """Consent form was not signed or was declined"""

    pass


class LocationExistsError(AzoteaError):
    """Location already exists"""

    pass


class LocationMissingError(AzoteaError):
    """Location does not exists"""

    pass

class MissingDefaultLocationError(AzoteaError):
    """Default location is not set"""

    pass


class ObserverExistsError(AzoteaError):
    """Observer already exists"""

    pass


class ObserverMissingError(AzoteaError):
    """Observer does not exists"""

    pass

class MissingDefaultObserverError(AzoteaError):
    """Default observer is not set"""

    pass



class CameraExistsError(AzoteaError):
    """Camera already exists"""

    pass


class CameraMissingError(AzoteaError):
    """Camera does not exists"""

    pass

class MissingDefaultCameraError(AzoteaError):
    """Default camera is not set"""

    pass

class RoiExistsError(AzoteaError):
    """Roi already exists"""

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
