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
