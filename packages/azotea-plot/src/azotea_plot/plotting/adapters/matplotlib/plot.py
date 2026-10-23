# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from collections.abc import Sequence
from math import ceil, sqrt

# ---------------------
# Third party libraries
# ---------------------
from lica_raw import BayerIndex
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as patches

# ----------------
# Own dependencies
# ----------------
from ... import ImagePlotSpec, PlotConfig, RawImagePlotter

# ---------
# Constants
# ---------

# For colormaps, see: https://matplotlib.org/stable/users/explain/colors/colormaps.html

IMAGE_CMAP = {
    BayerIndex.R: "hot",
    BayerIndex.Gr: "summer",
    BayerIndex.Gb: "summer",
    BayerIndex.B: "winter",
}
CONTOUR_CMAP = {
    BayerIndex.R: "prism",
    BayerIndex.Gr: "prism",
    BayerIndex.Gb: "flag",
    BayerIndex.B: "flag",
}
EDGE_COLOR = {BayerIndex.R: "y", BayerIndex.Gr: "b", BayerIndex.Gb: "b", BayerIndex.B: "r"}

# Load global style sheets

plt.style.use("azotea_plot.plotting.adapters.matplotlib.global")

def plot_contour_cmap(channels):
    """Plot image color map of channels to display"""
    return [CONTOUR_CMAP[ch] for ch in channels]


def plot_layout(channels):
    """Plot layout dimensions  as a function of channels to display"""
    # returns (nrows, ncols)
    return LAYOUT[len(channels)]


def plot(axes: Axes, data: ImagePlotSpec) -> None:
    cmap = IMAGE_CMAP[data.bayer]
    edgecolor = EDGE_COLOR[data.bayer]
    axes.set_title(rf"{data.bayer.name} channel: {data.section} $\mu={data.mean:.2f}, \sigma={data.stddev:.2f}$")
    # we choose an statistical visualization or else the min max/data range
    vmax = data.mean + 3 * data.stddev if data.display_max is None else data.display_max
    vmin = data.mean - 1 * data.stddev if data.display_min is None else data.display_min
    img = axes.imshow(data.image, cmap=cmap, vmin=vmin, vmax=vmax)
    # Create the Rectangle patch for the standard ROI
    rect = patches.Rectangle(
        data.section.origin,
        data.section.width,
        data.section.height,
        linewidth=1,
        linestyle="--",
        edgecolor=edgecolor,
        facecolor="none",
    )
    axes.add_patch(rect)
    divider = make_axes_locatable(axes)
    cax = divider.append_axes("right", size="5%", pad=0.10)
    axes.get_figure().colorbar(img, cax=cax, orientation="vertical")

class MplRawImagePlotter(RawImagePlotter):

    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig, title: str | None = None) -> None:
        config.apply()
        # this is overengineering for a 2x2 case
        # # but wanted to try generic code
        n = len(data)
        cols = ceil(sqrt(n))
        rows = ceil(n / cols)
        fig, axes = plt.subplots(nrows=rows, ncols=cols)
        axes = axes.ravel() # aplana el array
        if title is not None:
            fig.suptitle(title)
        for i, (axe, _data) in enumerate(zip(axes, data)):
            if i >= n:
                axe.set_axis_off()
            plot(axe, _data)
        plt.show()
