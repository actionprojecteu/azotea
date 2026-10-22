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
from ... import PlotConfig


class NoPlotConfig(PlotConfig):
    def apply(self):
        pass
