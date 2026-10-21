import logging
from collections.abc import Sequence
from .. import PlotConfig, ImagePlotSpec, RawImagePlotter


log = logging.getLogger(__name__.split(".")[-1])


class MockPlotConfig(PlotConfig):
    def apply(self) -> None:
        log.debug("calling MockPlotConfig.apply()")


class MockRawImagePlotter(RawImagePlotter):
   def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None:
       log.debug("calling MockPlotConfig.apply()")
       config.apply()
       log.debug(data)
