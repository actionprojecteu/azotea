import logging

from lica_raw import Rect

from ... import PlotConfig, RawImagePlotSet, RawImagePlotter

log = logging.getLogger(__name__.split(".")[-1])


class MockPlotConfig(PlotConfig):
    def apply(self):
        log.debug("calling MockPlotConfig.apply()")


class MockRawImagePlotter(RawImagePlotter):
    def plot(self, section: Rect, data: RawImagePlotSet, config: PlotConfig):
        log.debug("calling MockPlotConfig.apply()")
        config.apply()
        log.debug(section)
        log.debug(data)
