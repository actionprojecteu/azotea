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
from lica_raw import IntArray2D, Rect, BayerIndex

class ImagePlotSpec(NamedTuple):
    bayer: BayerIndex
    image: IntArray2D
    image_mean: float
    image_stddev: float
    image_min: int | None
    image_max: int | None
    image_sigmas_min: int
    image_sigmas_max: int
    section: Rect
    section_mean: float
    section_stddev: float
