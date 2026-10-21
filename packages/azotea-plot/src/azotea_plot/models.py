from dataclasses import dataclass
from typing import NamedTuple

from lica_raw import Rect

class Bounds(NamedTuple):
    low: int | None
    high: int | None

@dataclass(frozen=True)
class ScanForm:
    images_dir: str
    depth: int

@dataclass(frozen=True)
class PlotForm:
    section: Rect | None
    title: str | None
    sigma: float
    bounds: Bounds | None
