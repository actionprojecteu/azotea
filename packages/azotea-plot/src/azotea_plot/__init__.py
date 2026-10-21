# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("azotea-fits")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"
