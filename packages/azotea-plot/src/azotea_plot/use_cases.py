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


from lica_raw import ImageReaderFactory, Rect
from azotea_cli.common.filesystem import scan_images


from .models import  ScanForm, PlotForm
from .ports import EditorFactory

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


def plot_image(path: str, form: PlotForm, factory: ImageReaderFactory, plotter: RawImagePlotter, config: PlotterConfig) -> None:
    reader = factory.get_reader(path)
    #metadata = reader.read_metadata(path)
    with reader.read_pixels(path) as pixels:
        red_pixels = pixels.red(None)
        green_red = pixels.greenr(None)
        green_blue = pixels.greenb(None)
        red_pixels = pixels.blue(None)
        plotter.plot(title=os.path.basename(path), config=config)

def batch_plot_images(
    scan: ScanForm
) -> None:
    paths = scan_images(scan.images_dir, scan.depth, EXTENSIONS)
    for path in paths:
        show_fits_metadata(path, factory, display)
