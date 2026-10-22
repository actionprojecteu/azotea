# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from typing import NamedTuple

# ---------------------
# Third party libraries
# ---------------------
from lica_raw import IntArray2D, Rect


class ImagePlotSpec(NamedTuple):
    title: str
    image: IntArray2D
    section: Rect
    mean: float
    stddev: float
    display_min: int | None
    display_max: int | None
