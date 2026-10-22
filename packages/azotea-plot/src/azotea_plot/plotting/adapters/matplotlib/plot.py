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
import matplotlib as mpl
from lica_raw import BayerIndex, Rect
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
plt.style.use("rawplot.resources.global")
def plot_contour_cmap(channels):
    """Plot image color map of channels to display"""
    return [CONTOUR_CMAP[ch] for ch in channels]


def plot_image_cmap(channels):
    """Plot image color map of channels to display"""
    return [IMAGE_CMAP[ch] for ch in channels]


def plot_edge_color(channels):
    """Plot color map of channels to display"""
    return [EDGE_COLOR[ch] for ch in channels]


def plot_layout(channels):
    """Plot layout dimensions  as a function of channels to display"""
    # returns (nrows, ncols)
    return LAYOUT[len(channels)]


def axes_reshape(axes, channels):
    """Reshape Axes to be 2D arrays for 1x1 and 1x2 layout situations"""
    if len(channels) == 1:
        return np.array([axes]).reshape(-1, 1)
    if len(channels) == 2:
        return axes.reshape(-1, 2)
    return axes

def plot(axes: Axes, data: ImagePlotSpec) -> None:
    img_cmap = plot_image_cmap(channels)[i]
    edgecolor = plot_edge_color(channels)[i]

    title = rf"{channels[i]}: median={median:.2f}, $\mu={mean:.2f}, \sigma={stddev:.2f}$"
    axes.set_title(title)
    # we choose an statistical visualization or else the min max/data range
    if vstretch:
        vmax = vmean + 3 * vstd
        vmin = vmean - 1 * vstd
    im = axes.imshow(pixels, cmap=img_cmap, vmin=vmin, vmax=vmax)
    # Create the Rectangle patch for the standard ROI
    rect = patches.Rectangle(
        roi.xy(),
        roi.width(),
        roi.height(),
        linewidth=1,
        linestyle="--",
        edgecolor=edgecolor,
        facecolor="none",
    )
    axes.add_patch(rect)
    # Create more Rectangle patches for optional extended ROIs

    divider = make_axes_locatable(axes)
    cax = divider.append_axes("right", size="5%", pad=0.10)
    axes.get_figure().colorbar(im, cax=cax, orientation="vertical")

class MplRawImagePlotter(RawImagePlotter):

    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None:
        config.apply()
        # this is overengineering for a 2x2 case
        # # but wanted to try generic code
        n = len(data)
        cols = ceil(sqrt(n))
        rows = ceil(n / cols)
        _fig, axes = plt.subplots(nrows=rows, ncols=cols)
        for i, (axe, _data) in enumerate(zip(axes, data)):
            if i >= n:
                axe.set_axis_off()
            plot(axe, _data)
