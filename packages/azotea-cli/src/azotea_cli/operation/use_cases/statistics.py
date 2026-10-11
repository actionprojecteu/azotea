# ------------------
# standard libraries
# ------------------

import logging
import os
from datetime import datetime, timezone
from itertools import batched

# ---------------------
# Third party libraries
# ---------------------
#
# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.reader import ImageReaderFactory
from azotea_cli.provision.errors import CameraMissingError
from azotea_cli.provision.interfaces import (
    CameraRepo,
    ConsentRepo,
    ObserverRepo,
    RoiRepo,
)

from ..errors import CameraNotDefaultError, MissingTimestampError
from ..interfaces import SkyBrightnessRepo, ImagesRepo
from ..models import ImageForm, RegisterForm

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

class SkyStatisticsUseCase:
    BATCH_SIZE: int = 100

    def __init__(
        self,
        consent: ConsentRepo,
        camera: CameraRepo,
        observer: ObserverRepo,
        roi: RoiRepo,
        factory: ImageReaderFactory,
        images: ImagesRepo,
        sky_stats: SkyBrightnessRepo,
    ) -> None:
        self.consent = consent
        self.camera = camera
        self.observer = observer
        self.roi = roi
        self.factory = factory
        self.images = images
        self.sky_stats = sky_stats

    def compute_sky_statistics(self) -> None:
        self.consent.check_raises()
        log.info("computing sky background statistics")
        observer_id = self.observer.get_default()
        self.roi_id = self.roi.get_default()
        pending_image_ids = self.repo.pending_processing_by(observer_id)
