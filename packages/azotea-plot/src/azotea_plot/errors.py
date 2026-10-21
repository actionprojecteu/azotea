# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
class AzoteaPlotError(Exception):
    """AzoteaPlotError"""

    def __str__(self):
        msg = self.__doc__
        return f"{msg}: {self.args[0]}." if self.args else f"{msg}."
