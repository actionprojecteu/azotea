import logging

from astropy.io import fits

from azotea_cli.common.filesystem import scan_images
from azotea_cli.common.display.ports import DisplayService

from .models import FitsForm, ScanForm, EXTENSIONS
from .ports import EditorFactory


# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

def show_file_metadata(path: str,  factory: EditorFactory, display: DisplayService) -> None:
    editor = factory.get_editor(path)
    with fits.open(path) as hdul:
        data = editor.read.keywords(hdul[0].header)
        display.show_tabular(data, keys=("Field","Keyword","Value"))

def show_files_metadata(scan: ScanForm,  factory: EditorFactory, display: DisplayService) -> None:
    paths = scan_images(scan.images_dir, scan.depth, EXTENSIONS)
    for path in paths:
        show_file_metadata(path, factory, display)


def set_software_creator(path: str, name: str, factory: EditorFactory) -> None:
    pass


def edit_fits_file(path: str, form: FitsForm, factory: EditorFactory) -> None:
    editor = factory.get_editor(path)
    with fits.open(path, mode='update') as hdul:
        header = hdul[0].header
        history = list()
        log.info("-" * 57)
        editor.fix.camera(header, history)
        editor.fix.gain(header, history)
        editor.fix.xpixsize(header, history)
        editor.fix.ypixsize(header, history)
        editor.fix.bayer(header, history)
        editor.fix.bias(header, history)
        editor.fix.image_type(header, history)
        editor.fix.diameter(header, history)
        editor.fix.focal_length(header, history)
        editor.fix.exptime(header, history)
        editor.fix.date_obs(header, history)
        editor.fix.add_history(header, history)
        history = list()
        editor.edit.camera(header, form.camera, history)
        editor.edit.gain(header, form.gain, history)
        editor.edit.xpixsize(header, form.x_pixsize, history)
        editor.edit.ypixsize(header, form.y_pixsize, history)
        editor.edit.bayer(header, form.bayer_pattern, history)
        editor.edit.bias(header, form.bias, history)
        editor.edit.image_type(header, form.image_type, history)
        editor.edit.diameter(header, form.diameter, history)
        editor.edit.focal_length(header, form.focal_length, history)
        editor.edit.exptime(header, form.exptime, history)
        editor.edit.date_obs(header, form.date_obs, history)
        editor.edit.add_history(header, history)


def edit_fits_files(scan: ScanForm, form: FitsForm, factory: EditorFactory) -> None:
    paths = scan_images(scan.images_dir, scan.depth, EXTENSIONS)
    for path in paths:
        edit_fits_file(path, form, factory)
