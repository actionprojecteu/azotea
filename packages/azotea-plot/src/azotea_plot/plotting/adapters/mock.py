# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import logging
from collections.abc import Sequence

# ----------------
# Own dependencies
# ----------------
from .. import ImagePlotSpec, PlotConfig, RawImagePlotter

log = logging.getLogger(__name__.split(".")[-1])


class MockPlotConfig(PlotConfig):
    def apply(self) -> None:
        log.debug("calling MockPlotConfig.apply()")


class MockRawImagePlotter(RawImagePlotter):
    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None:
        log.debug("calling MockPlotConfig.apply()")
        config.apply()
        log.debug(data)
