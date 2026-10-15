
from astropy.io import fits

from ..ports import EditorFactory, Editor, SWCREATOR
from .generic import GenericMetadataFix, GenericMetadataInsert
from .capturafits import CapturaFitsMetadataFix, CapturaFitsMetadataInsert
from .sharpcap import SharpCapMetadataFix, SharpCapMetadataInsert

from ..enums import SwCreator

class EditorFactoryImpl(EditorFactory):

     def build_editor(self, path: str) -> Editor:
        with fits.open(path) as hdul:
            header = hdul[0].header
            swcreator = header.get(SWCREATOR)
            try:
                swcreator = SwCreator(swcreator)
            except Exception:
                return Editor(fix=GenericMetadataFix(), edit=GenericMetadataInsert())
            else:
                if swcreator == SwCreator.SHARPCAP:
                    return Editor(fix=SharpCapMetadataFix(), edit=SharpCapMetadataInsert())
                elif swcreator == SwCreator.CAPTURAFITS:
                    return Editor(fix=CapturaFitsMetadataFix(), edit=CapturaFitsMetadataInsert())
                else:
                    raise NotImplementedError("missing FITS editor")
