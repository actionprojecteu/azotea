
import matplotlib as mpl
from matplotlib import pyplot as plt

from lica_raw import Rect

from .. import PlotConfig, RawImagePlotSet, RawImagePlotter

# Load global style sheets
plt.style.use("rawplot.resources.global")


class MplRawImagePlotter(RawImagePlotter):
    def plot(self, section: Rect, data: RawImagePlotSet, config: PlotConfig) -> None:
        config.apply()
