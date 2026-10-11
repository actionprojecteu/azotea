# ------------------
# standard libraries
# ------------------
#
import logging
import os
from collections.abc import Sequence
from datetime import datetime

# ---------------------
# Third party libraries
# ---------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.infra.sqlalchemy import Image, get_db_session

# from ..errors import
from ..interfaces import ImagesRepo
from ..models import ImageForm

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__.split(".")[-1])


class ImagesRepoImpl(ImagesRepo):
    def get_stored_image_paths(self) -> list[str]:
        with get_db_session() as session:
            sql = select(Image.directory, Image.name)
            result = session.execute(sql).all()
            return [os.path.join(path[0], path[1]) for path in result]

    def date_time_ids(self, tstamp: datetime) -> tuple[int, int]:
        date_id = int(tstamp.strftime("%Y%m%d"))
        time_id = int(tstamp.strftime("%H%M%S"))
        return date_id, time_id

    def _translate(self, image: ImageForm) -> Image:
        date_id, time_id = self.date_time_ids(image.date_obs)
        return Image(
            name=image.name,
            directory=image.directory,
            hash=image.hash,
            iso=image.iso,
            gain=image.gain,
            exptime=image.exptime,
            focal_length=image.focal_length,
            f_number=image.f_number,
            imagetype=image.imagetype,
            flagged=image.flagged,
            session=int(image.session),
            camera_id=image.camera_id,
            observer_id=image.observer_id,
            location_id=image.location_id,
            date_id=date_id,
            time_id=time_id,
        )

    def save_one_by_one(self, images: Sequence[ImageForm]) -> None:
        for image in images:
            try:
                with get_db_session() as session:
                    with session.begin():
                        session.add(self._translate(image))
            except IntegrityError:
                log.warning(
                    "Skipping image already present or violating a constraint: %s",
                    image.name,
                    exc_info=True,
                )

    def save_images(self, images: Sequence[ImageForm]) -> None:
        with get_db_session() as session:
            try:
                with session.begin():
                    for image in images:
                        session.add(self._translate(image))
            except IntegrityError:
                log.warning("error saving a batch of %d images, looping one by one", len(images))
                self.save_one_by_one(images)
