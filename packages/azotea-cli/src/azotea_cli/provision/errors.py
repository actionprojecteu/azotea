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


class ObserverExistsError(AzoteaError):
    """Observer already exists"""

    pass


class ObserverMissingError(AzoteaError):
    """Observer does not exists"""

    pass


class CameraExistsError(AzoteaError):
    """Camera already exists"""

    pass


class CameraMissingError(AzoteaError):
    """Camera does not exists"""

    pass


__all__ = [
    "ConsentNotAgreedError",
    "LocationExistsError",
    "LocationMissingError",
    "ObserverExistsError",
    "ObserverMissingError",
    "CameraExistsError",
    "CameraMissingError",
]
