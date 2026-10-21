from typing import NamedTuple
from lica_raw import IntArray2D, Rect

class ImagePlotSpec(NamedTuple):
    title: str
    image: IntArray2D
    section: Rect
    mean: float
    stddev: float
    display_min: int | None
    display_max: int | None
