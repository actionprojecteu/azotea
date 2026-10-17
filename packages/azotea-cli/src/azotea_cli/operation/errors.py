# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.errors import AzoteaError


class CameraNotDefaultError(AzoteaError):
    """Image metadata camera is not the default camera"""


class MissingTimestampError(AzoteaError):
    """Image does not contain an observation date"""
