# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging
import os
from itertools import batched

# ---------------------
# Third party libraries
# ---------------------
import numpy as np
from lica_raw import ImageReaderFactory, MissingImageError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.errors import AzoteaError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.types import ObjId
from azotea_cli.provision.ports import (
    CameraRepo,
    ConsentService,
    ObserverRepo,
    RoiRepo,
)

from azotea_cli.operation.ports import ImagesRepo, SkyBrightnessRepo
from azotea_cli.operation.models import SkyStatsForm

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class ComputeSkyStatistics:
    BATCH_SIZE: int = 100

    def __init__(
        self,
        consent: ConsentService,
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

    def _one_pass(self, image_id: ObjId, path: str) -> SkyStatsForm:
        reader = self.factory.get_reader(path)
        with reader.read_pixels(path) as raw_pixels:
            red = raw_pixels.red(self.section)
            green_r = raw_pixels.greenr(self.section)
            green_b = raw_pixels.greenb(self.section)
            blue = raw_pixels.blue(self.section)
            stats = SkyStatsForm(
                image_id=image_id,
                roi_id=self.roi_id,
                aver_signal_R=np.mean(red),
                vari_signal_R=np.var(red),
                aver_signal_G1=np.mean(green_r),
                vari_signal_G1=np.var(green_r),
                aver_signal_G2=np.mean(green_b),
                vari_signal_G2=np.var(green_b),
                aver_signal_B=np.mean(blue),
                vari_signal_B=np.var(blue),
            )
            log.debug("black level R %d", raw_pixels.red_black_level())
            log.debug("black level Gr %d", raw_pixels.greenr_black_level())
            log.debug("black level Gb %d", raw_pixels.greenb_black_level())
            log.debug("black level B %d", raw_pixels.blue_black_level())
        return stats

    def execute(self) -> None:
        self.consent.check_raises()
        log.info("computing sky background statistics")
        observer_id = self.observer.get_default()
        self.roi_id = self.roi.get_default()
        self.section = self.roi.get_as_rect(self.roi_id)
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
                        "sky stats for %s [%d/%d] (%d%%)",
                        os.path.basename(path),
                        i,
                        n_selected,
                        perc,
                    )
                    stats = self._one_pass(image_id, path)
                except (AzoteaError, MissingImageError) as e:
                    n_skipped += 1
                    log.warning("%s, skipping", e)
                    continue
                else:
                    statistics.append(stats)
            log.info("saving a batch of %d images", len(statistics))
            self.sky_stats.save_statistics(statistics)
        log.info(
            "%d image statistics selected, %d computed, %d discarded",
            n_selected,
            n_selected - n_skipped,
            n_skipped,
        )
