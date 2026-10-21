from typing import NamedTuple
from lica_raw import IntArray2D

class RawImagePlotItem(NamedTuple):
   channel: IntArray2D
   sigma: float

class RawImagePlotSet(NamedTuple):
    red: RawImagePlotItem
    green_r: RawImagePlotItem
    blue: RawImagePlotItem
    green_b: RawImagePlotItem
