# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging

from astropy.io import fits

from ..enums import SwCreator
from ..models import SWCREATOR
from ..ports import Editor, EditorFactory
from .capturafits import CapturaFitsMetadataFix, CapturaFitsMetadataInsert
from .generic import GenericMetadataFix, GenericMetadataInsert, GenericMetadataLookup
from .sharpcap import SharpCapMetadataFix, SharpCapMetadataInsert

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class EditorFactoryImpl(EditorFactory):
    def get_editor(self, path: str) -> Editor:
        with fits.open(path) as hdul:
            header = hdul[0].header  # pyright: ignore[reportAttributeAccessIssue]
            swcreator = header.get(SWCREATOR)
            try:
                swcreator = SwCreator(swcreator.lower())
            except Exception:
                log.warning("Creating the generic FITS editor")
                return Editor(
                    fix=GenericMetadataFix(path),
                    edit=GenericMetadataInsert(path),
                    read=GenericMetadataLookup(),
                )
            else:
                if swcreator == SwCreator.SHARPCAP:
                    log.info("Creating the %s FITS editor", str(swcreator))
                    return Editor(
                        fix=SharpCapMetadataFix(path),
                        edit=SharpCapMetadataInsert(path),
                        read=GenericMetadataLookup(),
                    )
                elif swcreator == SwCreator.CAPTURAFITS:
                    log.info("Creating the %s FITS editor", str(swcreator))
                    return Editor(
                        fix=CapturaFitsMetadataFix(path),
                        edit=CapturaFitsMetadataInsert(path),
                        read=GenericMetadataLookup(),
                    )
                else:
                    raise NotImplementedError("missing FITS editor")
