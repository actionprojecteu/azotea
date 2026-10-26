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
from collections.abc import MutableSequence, Sequence
from dataclasses import fields
from datetime import datetime
from typing import Any

from astropy.io.fits import Header
from lica_raw import BayerPattern, ImageType
from lica_raw.adapters.fits import (
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
    PEDESTAL,
    XPIXSIZE,
    YPIXSIZE,
)

from ..models import SWCREATOR, FitsData, FitsKeyword
from ..ports import MetadataFix, MetadataInsert, MetadataLookup

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


def edit_keyword(
    header: Header, keyword: str, value: Any | None, comment: str | None, name: str
) -> str | None:
    msg = None
    if value is None:
        return msg
    old_value = header.get(keyword)
    if old_value is None:
        header[keyword] = value
        msg = f"added {keyword} keyword"
        log.info("%s: %s", name, msg)
    elif old_value != value:
        msg = f"{keyword}: {old_value} => {value} by azofits"
        log.info("%s: %s", name, msg)
        if comment:
            header[keyword] = (value, comment)
        else:
            header[keyword] = value
    return msg


class GenericMetadataFix(MetadataFix):
    """Review and edit existing keyword values in-place"""

    def __init__(self, path: str) -> None:
        self.path = path
        self.name = os.path.basename(path)

    def camera(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place camera model editing. Changes are annotated in the history mutable sequence"""

    def gain(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place CMOS gain editing. Changes are annotated in the history mutable sequence"""

    def xpixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'x' pixel size editing. Changes are annotated in the history mutable sequence"""

    def ypixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place 'y' pixel size editing. Changes are annotated in the history mutable sequence"""

    def bayer(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place bayer pattern editing. Changes are annotated in the history mutable sequence"""

    def bias(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place overal biass level editing. Changes are annotated in the history mutable sequence"""

    def image_type(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place image type editing. Changes are annotated in the history mutable sequence"""

    def diameter(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place aperture diameter editing. Changes are annotated in the history mutable sequence"""

    def focal_length(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place focal editing. Changes are annotated in the history mutable sequence"""

    def exptime(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place exposure time editing. Changes are annotated in the history mutable sequence"""

    def date_obs(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place observation date editing. Changes are annotated in the history mutable sequence"""

    def add_history(self, header: Header, history: Sequence[str | None]) -> None:
        """Add the in-place edition history"""
        for item in history:
            if item is not None:
                header[HISTORY] = item


class GenericMetadataInsert(MetadataInsert):
    def __init__(self, path: str) -> None:
        self.path = path
        self.name = os.path.basename(path)

    def camera(
        self,
        header: Header,
        value: str | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, INSTRUME, value, "Camera model", self.name)
        history.append(h)

    def gain(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, LOG_GAIN, value, "amplifer gain, log scale", self.name)
        history.append(h)

    def xpixsize(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, XPIXSIZE, value, "[um]", self.name)
        history.append(h)

    def ypixsize(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, YPIXSIZE, value, "[um]", self.name)
        history.append(h)

    def bayer(
        self,
        header: Header,
        value: BayerPattern | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, BAYERPAT, value, "bayer pattern", self.name)
        history.append(h)

    def bias(
        self,
        header: Header,
        value: int | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, PEDESTAL, value, "overall bias", self.name)
        history.append(h)

    def image_type(
        self,
        header: Header,
        value: ImageType | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, IMAGETYP, value, None, self.name)
        history.append(h)

    def diameter(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, APTDIA, value, "[mm]", self.name)
        history.append(h)

    def focal_length(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, FOCALLEN, value, "[mm]", self.name)
        history.append(h)

    def exptime(
        self,
        header: Header,
        value: float | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, EXPTIME, value, "[s]", self.name)
        history.append(h)

    def date_obs(
        self,
        header: Header,
        value: datetime | None,
        history: MutableSequence[str | None],
    ) -> None:
        h = edit_keyword(header, DATE_OBS, value, "[UTC]", self.name)
        history.append(h)

    def sw_creator(
        self, header: Header, value: str | None, history: MutableSequence[str | None]
    ) -> None:
        keyword = SWCREATOR
        msg = None
        if value is None:
            return msg
        old_value = header.get(keyword)
        old_value = str(old_value) if old_value is not None else None
        if old_value is None:
            header[keyword] = value
            msg = f"added {keyword} keyword"
            log.info("%s: %s", self.name, msg)
        elif old_value.lower() != value.lower():
            msg = f"{keyword}: {old_value} => {value} by azofits"
            log.info("%s: %s", self.name, msg)
            header[keyword] = value

    def comment(self, header: Header, value: str | None) -> None:
        if value is not None:
            header[COMMENT] = value

    def add_history(self, header: Header, history: Sequence[str]) -> None:
        """Add the edition history"""
        for item in history:
            if item is not None:
                header["HISTORY"] = item


class GenericMetadataLookup(MetadataLookup):

    def keywords(self, header: Header) -> Sequence[FitsKeyword]:
        data = FitsData(
            camera=str(header.get(INSTRUME)),
            bayer_pattern=str(header.get(BAYERPAT)),
            gain=str(header.get(LOG_GAIN)),
            bias=str(header.get(PEDESTAL)),
            x_pixsize=str(header.get(XPIXSIZE)),
            y_pixsize=str(header.get(YPIXSIZE)),
            image_type=str(header.get(IMAGETYP)),
            diameter=str(header.get(APTDIA)),
            focal_length=str(header.get(FOCALLEN)),
            date_obs=str(header.get(DATE_OBS)),
            exptime=str(header.get(EXPTIME)),
            swcreator=str(header.get(SWCREATOR)),
        )
        return tuple((f.name, f.metadata["fits"], getattr(data, f.name)) for f in fields(data))
