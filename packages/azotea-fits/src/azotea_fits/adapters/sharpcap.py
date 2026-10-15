import logging
import os
import re
from collections.abc import MutableSequence

from astropy.io.fits import Header
from azotea_cli.common.reader.adapters.fits import (
    BAYERPAT,
    DATE_OBS,
    INSTRUME,
    LOG_GAIN,
    XPIXSIZE,
    YPIXSIZE,
)

from .generic import GenericMetadataFix, GenericMetadataInsert

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class SharpCapMetadataFix(GenericMetadataFix):
    CAMERA_RE = re.compile(r"(?m)^\[([^\]]+)\]")

    def __init__(self, path) -> None:
        super().__init__(path)
        file_name, _ = os.path.splitext(os.path.basename(path))
        aux_file = os.path.join(os.path.dirname(path), file_name + ".CameraSettings.txt")
        with open(aux_file) as fd:
            self.contents = fd.readlines()

    def _parse_camera(self) -> str | None:
        """Parse camera name from the auxiliary file."""
        if self.contents is None:
            return None
        for line in self.contents:
            if match := self.CAMERA_RE.match(line):
                return match.group(1)
        return None

    def _parse_gain(self) -> float | None:
        """Parse CMOS log gain from the auxiliary file."""
        if self.contents is None:
            return None
        for line in self.contents:
            if line.startswith("Gain="):
                try:
                    return float(line.removeprefix("Gain=").strip().replace(",", "."))
                except ValueError:
                    continue
        return None

    def camera(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place camera model editing. Changes are annotated in the history mutable sequence"""
        log.debug("fixing %s", INSTRUME)
        if header.get(INSTRUME) is None:
            camera = self._parse_camera()
            if camera is not None:
                header[INSTRUME] = camera
                msg = f"added {INSTRUME} keyword"
                log.info("%s: %s", self.name, msg)
                history.append(msg)

    def gain(self, header: Header, history: MutableSequence[str | None]) -> None:
        """In place CMOS gain editing. Changes are annotated in the history mutable sequence"""
        log.debug("fixing %s", LOG_GAIN)
        if header.get(LOG_GAIN) is None:
            camera = self._parse_gain()
            if camera is not None:
                header[LOG_GAIN] = camera
                msg = f"added {LOG_GAIN} keyword"
                log.info("%s: %s", self.name, msg)
                history.append(msg)

    def xpixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        keyword = XPIXSIZE
        log.debug("fixing %s", keyword)
        oldpixsz = header.get(keyword)
        if oldpixsz is not None:
            pixsz = round(float(oldpixsz), 2)
            if oldpixsz != pixsz:
                header[keyword] = pixsz
                header.comments[keyword] = "[um]"
                msg = f"{keyword} rounded to 2 decimals"
                history.append(msg)
                log.info("%s: %s", self.name, msg)

    def ypixsize(self, header: Header, history: MutableSequence[str | None]) -> None:
        keyword = YPIXSIZE
        log.debug("fixing %s", keyword)
        oldpixsz = header.get(keyword)
        if oldpixsz is not None:
            pixsz = round(float(oldpixsz), 2)
            if oldpixsz != pixsz:
                header[keyword] = pixsz
                header.comments[keyword] = "[um]"
                msg = f"{keyword} rounded to 2 decimals"
                history.append(msg)
                log.info("%s: %s", self.name, msg)

    def bayer(self, header: Header, history: MutableSequence[str | None]) -> None:
        old_keyw_x = "BAYOFFX"
        old_keyw_y = "BAYOFFY"
        new_keyw_x = "XBAYROFF"
        new_keyw_y = "XBAYROFF"
        value_x = header.get(old_keyw_x)
        value_y = header.get(old_keyw_x)
        first_time = all([value_x is not None, value_y is not None])
        if first_time:
            del header[old_keyw_x]
            del header[old_keyw_y]
            header[new_keyw_x] = value_x
            header[new_keyw_y] = value_y
            msg = f"subst. {old_keyw_x}->{new_keyw_x}, {old_keyw_y}->{new_keyw_y}"
            log.info(msg)
            history.append(msg)
        bayer_pat = header.get(BAYERPAT)
        if bayer_pat is not None and first_time:
            bayer_pat_new = str(bayer_pat[2:4]) + str(bayer_pat[0:2])
            msg = f"flipped prev BAYERPAT & COLORTYP from {bayer_pat} to {bayer_pat_new}"
            header[BAYERPAT] = bayer_pat_new
            header["COLORTYP"] = bayer_pat_new
            log.info(msg)
            history.append(msg)

    def date_obs(self, header: Header, history: MutableSequence[str | None]) -> None:
        date_obs = header.get(DATE_OBS)
        if date_obs is not None and len(date_obs) > 19:
            header[DATE_OBS] = (date_obs[:19], "UTC")
            msg = f"stripped microseconds in {DATE_OBS} keyword"
            log.info(msg)
            history.append(msg)


class SharpCapMetadataInsert(GenericMetadataInsert):
    pass
