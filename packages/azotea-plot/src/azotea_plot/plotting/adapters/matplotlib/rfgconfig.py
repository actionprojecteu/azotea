# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
# ----------------
# Own dependencies
# ----------------
import matplotlib as mpl
from matplotlib import pyplot as plt

from ... import PlotConfig


class RfgPlotConfig(PlotConfig):
    def apply(self):
        mpl.rcParams["text.usetex"] = False
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = ["Verdana"]
        plt.rcParams["font.size"] = 8
        plt.rcParams["lines.linewidth"] = 4.0
        plt.rcParams["axes.labelsize"] = "small"
        plt.rcParams["grid.linewidth"] = 1.0
        plt.rcParams["grid.linestyle"] = ":"
        plt.rcParams["xtick.minor.size"] = 4
        plt.rcParams["xtick.major.size"] = 8
        plt.rcParams["ytick.minor.size"] = 4
        plt.rcParams["ytick.major.size"] = 8
        plt.rcParams["figure.figsize"] = 18, 9
        plt.rcParams["figure.subplot.bottom"] = 0.15
        plt.rcParams["ytick.labelsize"] = 10
        plt.rcParams["xtick.labelsize"] = 10
        mpl.rcParams["xtick.direction"] = "out"
