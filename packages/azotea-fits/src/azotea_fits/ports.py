
from collections.abc import MutableSequence, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from astropy.io.fits import Header
from azotea_cli.common.types import BayerPattern, ImageType

SWCREATOR = "SWCREATE"

class MetadataFix(Protocol):
    """Review and edit existing keyword values in-place"""

    def camera(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place camera model editing. Changes are annotated in the history mutable sequence"""
        ...

    def gain(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place CMOS gain editing. Changes are annotated in the history mutable sequence"""
        ...

    def xpixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'x' pixel sizeediting. Changes are annotated in the history mutable sequence"""
        ...

    def ypixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'y' pixel size editing. Changes are annotated in the history mutable sequence"""
        ...

    def bayer(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place bayer pattern editing. Changes are annotated in the history mutable sequence"""
        ...

    def bias(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place overal biass level editing. Changes are annotated in the history mutable sequence"""
        ...

    def image_type(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place image type editing. Changes are annotated in the history mutable sequence"""
        ...

    def diameter(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place aperture diameter editing. Changes are annotated in the history mutable sequence"""
        ...

    def focal_length(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place focal editing. Changes are annotated in the history mutable sequence"""
        ...

    def exptime(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place exposure time editing. Changes are annotated in the history mutable sequence"""
        ...

    def date_obs(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place observation date editing. Changes are annotated in the history mutable sequence"""
        ...

    def add_history(self, header: Header, history: Sequence[str | None]) -> None:
        """Add the in-place edition history"""
        for item in history:
            if item is not None:
                header["HISTORY"] = item


class MetadataInsert(Protocol):
    """Insert or replace keyword values"""

    def camera(
        self, header: Header, value: str | None, history: MutableSequence[str | None]
    ) -> None: ...

    def gain(
        self, header: Header, value: float | None, history: MutableSequence[str | None]
    ) -> None: ...

    def xpixsize(
        self, header: Header, value: float | None, history: MutableSequence[str | None]
    ) -> None: ...

    def ypixsize(
        self, header: Header, value: float | None, history: MutableSequence[str | None]
    ) -> None: ...

    def bayer(
        self, header: Header, value: BayerPattern | None, history: MutableSequence[str | None]
    ) -> None: ...
    def bias(
        self, header: Header, value: int | None, history: MutableSequence[str | None]
    ) -> None: ...

    def image_type(
        self, header: Header, value: ImageType | None, history: MutableSequence[str | None]
    ) -> None: ...

    def diameter(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None: ...

    def focal_length(
        self, header: Header, value: float | None, history: MutableSequence[str | None]
    ) -> None: ...

    def exptime(
        self, header: Header, value: float | None, history: MutableSequence[str | None]
    ) -> None: ...

    def date_obs(
        self, header: Header, value: datetime | None, history: MutableSequence[str | None]
    ) -> None: ...

    def comment(self, header: Header, value: str | None) -> None: ...

    def add_history(self, header: Header, history: Sequence[str]) -> None: ...


@dataclass(frozen=True)
class Editor:
    fix: MetadataFix
    edit: MetadataInsert


class EditorFactory(Protocol):
    def build_editor(self, path: str) -> Editor: ...
