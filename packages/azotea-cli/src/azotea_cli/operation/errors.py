from azotea_cli.common.errors import AzoteaError


class CameraNotDefaultError(AzoteaError):
    """Image metadata camera is not the default camera"""

    pass


class MissingTimestampError(AzoteaError):
    """Image does not contain an observation date"""

    pass
