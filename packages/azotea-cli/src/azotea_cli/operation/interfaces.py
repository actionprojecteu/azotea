from typing import Protocol
from collections.abc import Sequence

from .models import ImageForm

class ImagesRepo(Protocol):
    def get_stored_image_paths(self) -> list[str]: ...
    def save_images(self, images: Sequence[ImageForm]) -> None: ...
