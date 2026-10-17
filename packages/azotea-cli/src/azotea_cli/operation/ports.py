# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
from collections.abc import Sequence
from typing import Protocol

# ---------------
# Own dependecies
# ---------------
from azotea_cli.common.types import ObjId

from .models import ImageForm, SkyStatsForm


class ImagesRepo(Protocol):
    def get_stored_image_paths(self) -> Sequence[str]: ...
    def save_images(self, images: Sequence[ImageForm]) -> None: ...
    def pending_processing_by(self, observer_id: ObjId) -> Sequence[ObjId]: ...
    def to_paths(self, image_ids: Sequence[ObjId]) -> Sequence[str]: ...


class SkyBrightnessRepo(Protocol):
    def save_statistics(self, statistics: Sequence[SkyStatsForm]) -> None: ...
