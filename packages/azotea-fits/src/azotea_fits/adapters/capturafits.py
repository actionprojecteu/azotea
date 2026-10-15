import logging
import os
from collections.abc import MutableSequence
from datetime import datetime

from astropy.io.fits import Header
from azotea_cli.common.reader.adapters.fits import (
    DATE_OBS,
    EXPTIME,
)

from .generic import GenericMetadataFix, GenericMetadataInsert

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class CapturaFitsMetadataFix(GenericMetadataFix):
    def __init__(self, path) -> None:
        super().__init__(path)
        file_name = os.path.basename(path)
        datetime_txt, exptime_text, _ = file_name.split(".")
        self.exposure = round(float(exptime_text) / 1000, 2)
        self.timestamp = datetime.strptime(datetime_txt, "%Y%m%d-%H%M%S")

    def date_obs(self, header: Header, history: MutableSequence[str | None]) -> None:
        date_obs = header.get(DATE_OBS)
        if date_obs is None:
            header[DATE_OBS] = (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S"), "[UTC]")
            msg = f"stripped microseconds in {DATE_OBS} keyword"
            log.info(msg)
            history.append(msg)

    def exptime(self, header: Header, history: MutableSequence[str | None]) -> None:
        exptime = header.get(EXPTIME)
        if exptime is None:
            header[EXPTIME] = (self.exposure, "[s]")
            msg = f"added {DATE_OBS} keyword"
            log.info(msg)
            history.append(msg)


class CapturaFitsMetadataInsert(GenericMetadataInsert):
    pass
