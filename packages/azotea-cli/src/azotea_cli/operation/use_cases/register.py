# ------------------
# standard libraries
# ------------------

import logging
import os
from datetime import datetime, timezone
from itertools import batched
from typing import ParamSpecArgs

# ---------------------
# Third party libraries
# ---------------------
# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.reader import ImageReaderFactory
from azotea_cli.provision.errors import CameraMissingError
from azotea_cli.provision.interfaces import (
    CameraRepo,
    ConsentRepo,
    LocationRepo,
    ObserverRepo,
    OpticsRepo,
)

from ..errors import CameraNotDefaultError, MissingTimestampError
from ..filesystem import hash_func, scan_images
from ..interfaces import ImagesRepo
from ..models import ImageForm, RegisterForm

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class RegisterImagesUseCase:
    BATCH_SIZE: int = 100

    def __init__(
        self,
        consent: ConsentRepo,
        camera: CameraRepo,
        location: LocationRepo,
        observer: ObserverRepo,
        optics: OpticsRepo,
        factory: ImageReaderFactory,
        repository: ImagesRepo,
    ) -> None:
        self.consent = consent
        self.camera = camera
        self.location = location
        self.observer = observer
        self.optics = optics
        self.factory = factory
        self.repository = repository

    def one_pass(self, path: str) -> ImageForm:
        reader = self.factory.get_reader(path)
        metadata = reader.read_metadata(path, self.optics_info.focal_len, self.optics_info.f_number)
        if metadata.timestamp is None:
            raise MissingTimestampError(os.path.basename(path))
        # this may trigger an exception as well
        camera_id = self.camera.get_id_by_model(metadata.model)
        if camera_id != self.camera_id:
            raise CameraNotDefaultError()
        # we compute the expensive hash function only after we make sur ethat the camera estsis
        hash = hash_func(path)
        image = ImageForm(
            name=os.path.basename(path),
            directory=os.path.dirname(path),
            hash=hash,
            iso=metadata.iso,
            gain=metadata.gain,
            exptime=metadata.exptime,
            focal_length=metadata.focal_len,
            f_number=metadata.f_number,
            imagetype=metadata.imagetyp,
            flagged=False,
            session=self.session,
            date_obs=metadata.timestamp,
            camera_id=self.camera_id,
            observer_id=self.observer_id,
            location_id=self.location_id,
        )
        return image

    def register_images(self, form: RegisterForm) -> None:
        self.consent.check_raises()
        log.info("starting registration process")
        self.session = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        self.optics_info = self.optics.load()
        self.camera_id = self.camera.get_default()
        self.location_id = self.location.get_default()
        self.observer_id = self.observer.get_default()
        extension = self.camera.get_extension_by_id(self.camera_id)
        input_files = scan_images(form.images_dir, form.depth, extension)
        stored_files = self.repository.get_stored_image_paths()
        new_files = list(set(input_files) - set(stored_files))
        n_selected = len(new_files)
        n_skipped = 0
        i = 0
        for batch in batched(new_files, self.BATCH_SIZE):
            images: list[ImageForm] = list()
            for path in batch:
                i += 1
                perc = int(round(i * 100 / n_selected, 0))
                try:
                    log.info(
                        "registering %s [%d/%d] (%d%%)", os.path.basename(path), i, n_selected, perc
                    )
                    image = self.one_pass(path)
                except (CameraMissingError, MissingTimestampError, CameraNotDefaultError) as e:
                    n_skipped = +1
                    log.warning("%s, skipping", e)
                    continue
                else:
                    images.append(image)
            log.info("saving a batch of %d images to repository", len(images))
            self.repository.save_images(images)
        log.info(
            "%d images analyzed, %d discarded, %d stored",
            n_selected,
            n_skipped,
            n_selected - n_skipped,
        )
