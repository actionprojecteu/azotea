# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from collections.abc import Sequence
from typing import Protocol

# ----------------
# Own dependencies
# ----------------
from .models import ImagePlotSpec


class PlotConfig(Protocol):
    def apply(self) -> None: ...


class RawImagePlotter(Protocol):
    def plot(self, data: Sequence[ImagePlotSpec], config: PlotConfig) -> None: ...
