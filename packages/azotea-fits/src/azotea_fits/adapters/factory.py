from astropy.io import fits

from ..enums import SwCreator
from ..errors import MissingFitsFileError
from ..models import SWCREATOR
from ..ports import Editor, EditorFactory
from .capturafits import CapturaFitsMetadataFix, CapturaFitsMetadataInsert
from .generic import GenericMetadataFix, GenericMetadataInsert
from .sharpcap import SharpCapMetadataFix, SharpCapMetadataInsert


class EditorFactoryImpl(EditorFactory):
    def get_editor(self, path: str) -> Editor:
        with fits.open(path) as hdul:
            header = hdul[0].header
            swcreator = header.get(SWCREATOR)
            try:
                swcreator = SwCreator(swcreator)
            except Exception:
                return Editor(fix=GenericMetadataFix(path), edit=GenericMetadataInsert(path))
            else:
                if swcreator == SwCreator.SHARPCAP:
                    return Editor(fix=SharpCapMetadataFix(path), edit=SharpCapMetadataInsert(path))
                elif swcreator == SwCreator.CAPTURAFITS:
                    return Editor(fix=CapturaFitsMetadataFix(path), edit=CapturaFitsMetadataInsert(path))
                else:
                    raise NotImplementedError("missing FITS editor")
