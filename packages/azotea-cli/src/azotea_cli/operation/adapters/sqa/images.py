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
from collections.abc import Sequence
from datetime import datetime

# ---------------------
# Third party libraries
# ---------------------
from lica_sqa import Database
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.types import ObjId
from azotea_cli.infra.sqlalchemy import Image, SkyBrightness

from ...models import ImageForm

# from ...errors import
from ...ports import ImagesRepo

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__.split(".")[-1])


class SqaImagesRepo(ImagesRepo):
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_stored_image_paths(self) -> list[str]:
        with self.db.session() as session:
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
            flagged=False,
            session=int(image.session),
            camera_id=image.camera_id.id,
            observer_id=image.observer_id.id,
            location_id=image.location_id.id,
            date_id=date_id,
            time_id=time_id,
        )

    def _update(
        self,
        images: Sequence[ImageForm],
    ) -> None:
        with self.db.session() as session, session.begin():
            for image in images:
                sql =  select(Image).where(Image.hash == image.hash)
                existing = session.scalars(sql).one_or_none()
                if existing is None:
                    log.warning(
                        "Integrity error but no existing image found for hash %s",
                        image.hash,
                    )
                    continue
                log.warning(
                    "Changing image path from %s to %s",
                    os.path.join(existing.directory, existing.name),
                    os.path.join(image.directory, image.name),
                )
                existing.name = image.name
                existing.directory = image.directory
                session.add(existing)

    def _save_one_by_one(self, images: Sequence[ImageForm]) -> None:
        existing_images = []
        for image in images:
            with self.db.session() as session, session.begin():
                session.add(self._translate(image))
                try:
                    log.info("retrying %s", image.name)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    existing_images.append(image)
        self._update(existing_images)


    def save_images(self, images: Sequence[ImageForm]) -> None:
        with self.db.session() as session:
            try:
                with session.begin():
                    for image in images:
                        session.add(self._translate(image))
            except IntegrityError:
                log.warning("error saving a batch of %d images, looping one by one", len(images))
                self._save_one_by_one(images)

    def pending_processing_by(self, observer_id: ObjId) -> Sequence[ObjId]:
        sql = select(Image.image_id).where(
            Image.observer_id == observer_id.id,
            ~select(SkyBrightness.image_id)
            .where(SkyBrightness.image_id == Image.image_id)
            .exists(),
        )
        with self.db.session() as session:
            image_ids = [ObjId(img_id) for img_id in session.scalars(sql)]
        return image_ids

    def to_paths(self, image_ids: Sequence[ObjId]) -> Sequence[str]:
        image_ids2 = [obj.id for obj in image_ids]
        sql = select(Image.directory, Image.name).where(Image.image_id.in_(image_ids2))
        with self.db.session() as session:
            result = session.execute(sql).all()
        return [os.path.join(dir, name) for dir, name in result]
