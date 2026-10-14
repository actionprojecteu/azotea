from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from astropy.io.fits import Header
from azotea_cli.common.models import BayerPattern, ImageType


class MetadataFix(Protocol):
    def camera(self, header: Header) -> None:
        pass

    def gain(self, header: Header) -> None:
        pass

    def xpixsize(self, header: Header) -> None:
        pass

    def ypixsize(self, header: Header) -> None:
        pass

    def bayer(self, header: Header) -> None:
        pass

    def bias(self, header: Header) -> None:
        pass

    def image_type(self, header: Header) -> None:
        pass

    def diameter(self, header: Header) -> None:
        pass

    def focal_length(self, header: Header) -> None:
        pass

    def exptime(self, header: Header) -> None:
        pass

    def date_obs(self, header: Header) -> None:
        pass


class MetadataInsert(Protocol):
    def camera(self, header: Header, value: str | None) -> None: ...
    def gain(self, header: Header, value: float | None) -> None: ...
    def xpixsize(self, header: Header, value: float | None) -> None: ...
    def ypixsize(self, header: Header, value: float | None) -> None: ...
    def bayer(self, header: Header, value: BayerPattern | None) -> None: ...
    def bias(self, header: Header, value: int | None) -> None: ...
    def image_type(self, header: Header, value: ImageType | None) -> None: ...
    def diameter(self, header: Header, value: float | None) -> None: ...
    def focal_length(self, header: Header, value: float | None) -> None: ...
    def exptime(self, header: Header, value: float | None) -> None: ...
    def date_obs(self, header: Header, value: datetime | None) -> None: ...
    def comment(self, header: Header, value: str | None) -> None: ...


@dataclass(frozen=True)
class Editor:
    fix: MetadataFix
    edit: MetadataInsert


class EditorFactory(Protocol):
    def build_editor(self) -> Editor: ...
