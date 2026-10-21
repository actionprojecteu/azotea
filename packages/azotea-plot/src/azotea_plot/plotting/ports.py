from typing import Protocol
from lica_raw import Rect
from .models import RawImagePlotSet


class PlotConfig(Protocol):
    def apply(self): ...


class RawImagePlotter(Protocol):
    def plot(self, section: Rect, data: RawImagePlotSet, config: PlotConfig): ...
