from dataclasses import dataclass
from typing import NamedTuple


class Bounds(NamedTuple):
    low: int | None
    high: int | None

@dataclass(frozen=True)
class ScanForm:
    images_dir: str
    depth: int

@dataclass(frozen=True)
class PlotForm:
    x1: int | None
    y1: int | None
    width: int
    height: int
    title: str | None
    n_sigma: float
    bounds: Bounds | None
