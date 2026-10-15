import logging
from collections.abc import MutableSequence, Sequence
from datetime import datetime
from typing import Any

from astropy.io.fits import Header
from azotea_cli.common.reader.adapters.fits import (
    APTDIA,
    BAYERPAT,
    COMMENT,
    DATE_OBS,
    EXPTIME,
    FOCALLEN,
    HISTORY,
    IMAGETYP,
    INSTRUME,
    LOG_GAIN,
    NAXIS1,
    NAXIS2,
    PEDESTAL,
    XPIXSIZE,
    YPIXSIZE,
)
from azotea_cli.common.types import BayerPattern, ImageType

from ..ports import MetadataFix, MetadataInsert

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


def edit_keyword(
    header: Header, keyword: str, value: Any | None, comment: str | None
) -> str | None:
    msg = None
    if value is None:
        return msg
    old_value = header.get(keyword)
    if old_value is None:
        header[keyword] = value
        msg = f"added {keyword} keyword"
        log.info(msg)
    elif old_value != value:
        msg = f"{keyword}: {old_value} => {value} by azofits"
        header[keyword] = value
        if comment:
            header.comments[keyword] = comment
    return msg


class GenericMetadataFix(MetadataFix):
    """Review and edit existing keyword values in-place"""

    def camera(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place camera model editing. Changes are annotated in the history mutable sequence"""
        pass

    def gain(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place CMOS gain editing. Changes are annotated in the history mutable sequence"""
        pass

    def xpixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'x' pixel sizeediting. Changes are annotated in the history mutable sequence"""
        pass

    def ypixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'y' pixel size editing. Changes are annotated in the history mutable sequence"""
        pass

    def bayer(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place bayer pattern editing. Changes are annotated in the history mutable sequence"""
        pass

    def bias(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place overal biass level editing. Changes are annotated in the history mutable sequence"""
        pass

    def image_type(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place image type editing. Changes are annotated in the history mutable sequence"""
        pass

    def diameter(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place aperture diameter editing. Changes are annotated in the history mutable sequence"""
        pass

    def focal_length(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place focal editing. Changes are annotated in the history mutable sequence"""
        pass

    def exptime(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place exposure time editing. Changes are annotated in the history mutable sequence"""
        pass

    def date_obs(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place observation date editing. Changes are annotated in the history mutable sequence"""
        pass

    def add_history(self, header: Header, history: Sequence[str | None]) -> None:
        """Add the in-place edition history"""
        for item in history:
            if item is not None:
                header[HISTORY] = item


class GenericMetadataInsert(MetadataInsert):
    def camera(
        self,
        header: Header,
        value: str | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, INSTRUME, value, "Camera model")
        history.append(h)

    def gain(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, LOG_GAIN, value, "amplifer gain, log scale")
        history.append(h)

    def xpixsize(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, XPIXSIZE, value, "[um]")
        history.append(h)

    def ypixsize(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, YPIXSIZE, value, "[um]")
        history.append(h)

    def bayer(
        self,
        header: Header,
        value: BayerPattern | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, BAYERPAT, value, "bayer pattern")
        history.append(h)

    def bias(
        self,
        header: Header,
        value: int | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, PEDESTAL, value, "overall bias")
        history.append(h)

    def image_type(
        self,
        header: Header,
        value: ImageType | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, IMAGETYP, value, None)
        history.append(h)

    def diameter(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, APTDIA, value, "[mm]")
        history.append(h)

    def focal_length(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, FOCALLEN, value, "[mm]")
        history.append(h)

    def exptime(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, EXPTIME, value, "[s]")
        history.append(h)

    def date_obs(
        self,
        header: Header,
        value: datetime | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, DATE_OBS, value, "[UTC]")
        history.append(h)

    def comment(self, header: Header, value: str | None) -> None:
        if value is not None:
            header[COMMENT] = value

    def add_history(self, header: Header, history: Sequence[str]) -> None:
        """Add the edition history"""
        for item in history:
            if item is not None:
                header["HISTORY"] = item
