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
from azotea_cli.common.models import ObjId
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.reader import ImageReaderFactory
from azotea_cli.provision.interfaces import (
    CameraRepo,
    ConsentRepo,
    ObserverRepo,
    RoiRepo,
)

from ..interfaces import SkyBrightnessRepo, ImagesRepo
from ..models import SkyStatsForm

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

    def one_pass(self, image_id: ObjId, path: str) -> SkyStatsForm:
        raise AzoteaError("Not yet implemented")

    def compute_sky_statistics(self) -> None:
        self.consent.check_raises()
        log.info("computing sky background statistics")
        observer_id = self.observer.get_default()
        self.roi_id = self.roi.get_default()
        rect = self.roi.get_as_rect(self.roi_id)
        pending_image_ids = self.images.pending_processing_by(observer_id)
        pending_paths = self.images.to_paths(pending_image_ids)
        n_selected = len(pending_image_ids)
        n_skipped = 0
        i = 0
        for batch in batched(zip(pending_image_ids, pending_paths), self.BATCH_SIZE):
            statistics: list[SkyStatsForm] = list()
            for image_id, path in batch:
                i += 1
                perc = int(round(i * 100 / n_selected, 0))
                try:
                    log.info(
                        "sky stats for %s [%d/%d] (%d%%)", os.path.basename(path), i, n_selected, perc
                    )
                    stats = self.one_pass(image_id, path)
                except AzoteaError as e:
                    n_skipped += 1
                    log.warning("%s, skipping", e)
                    continue
                else:
                    statistics.append(stats)
            log.info("saving a batch of %d images", len(statistics))
            self.sky_stats.save_statistics(statistics)
            log.info(
                    "%d image statistics selected, %d discarded, %d computed",
                    n_selected,
                    n_skipped,
                    n_selected - n_skipped,
            )
