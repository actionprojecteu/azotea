from typing import NamedTuple


class ScanForm(NamedTuple):
    images_dir: str
    depth: int

class PlotForm(NamedTuple):
    x1: int | None
    y1: int | None
    width: int
    height: int
    n_sigma: float
    vmin: int | None
    vmax: int | None
