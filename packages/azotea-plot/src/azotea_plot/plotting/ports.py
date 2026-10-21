from typing import Protocol
from collections.abc import Sequence

from .models import ImagePlotSpec


class PlotConfig(Protocol):
    def apply(self) -> None: ...


class RawImagePlotter(Protocol):
    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None: ...
