# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from collections.abc import Sequence

# ---------------------
# Third party libraries
# ---------------------
import matplotlib as mpl
from lica_raw import Rect
from matplotlib import pyplot as plt

# ----------------
# Own dependencies
# ----------------
from ... import ImagePlotSpec, PlotConfig, RawImagePlotter

# Load global style sheets
plt.style.use("rawplot.resources.global")


class MplRawImagePlotter(RawImagePlotter):
    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None:
        config.apply()
