from dataclasses import dataclass
from datetime import datetime

from azotea_cli.common.models import ImageType


@dataclass(frozen=True)
class ObservationReport:
    version: str
    session: int
    observer: str
    acronym: str
    site_name: str
    location: str
    imagetype: ImageType
    date_obs: datetime
    image_name: str
    camera_model: str
    iso: int | None
    gain: float | None
    roi: str
    exptime: float
    aver_signal_r: float
    vari_signal_r: float
    aver_signal_g1: float
    vari_signal_g1: float
    aver_signal_g2: float
    vari_signal_g2: float
    aver_signal_b: float
    vari_signal_b: float
    bias: int


@dataclass(frozen=True)
class SummaryTotals:
    observer: str
    imagetype: ImageType
    flagged: bool
    count: int


@dataclass(frozen=True)
class SummaryRanged:
    observer: str
    display_name: str
    width: int
    height: int
    published: bool
    count: int
