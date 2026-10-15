from dataclasses import dataclass
from datetime import datetime

from azotea_cli.common.models import ImageType


@dataclass(frozen=True)
class ObservationReport:
    version: str
    session: int
    observer: str
    affiliation: str
    site_name: str
    location: str
    image_type: ImageType
    date_obs: datetime
    image_name: str
    camera_model: str
    iso: int | None
    gain: float | None
    roi: str
    exptime: float
    aver_signal_R: float
    vari_signal_R: float
    aver_signal_G1: float
    vari_signal_G1: float
    aver_signal_G2: float
    vari_signal_G2: float
    aver_signal_B: float
    vari_signal_B: float
    bias: int


@dataclass(frozen=True)
class SummaryTotals:
    observer: str
    image_type: ImageType
    flagged: bool
    count: int


@dataclass(frozen=True)
class SummaryRanged:
    observer: str
    roi: str
    width: int
    height: int
    published: bool
    count: int
