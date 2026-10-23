from typing import NamedTuple


class ScanForm(NamedTuple):
    images_dir: str
    depth: int

class PlotForm(NamedTuple):
    x1: int | None
    y1: int | None
    width: int
    height: int
    vmin: int | None
    vmax: int | None
    sigmas_min: int
    sigmas_max: int
