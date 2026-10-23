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

from matplotlib.cm import Reds
import numpy as np
from lica_raw import BayerIndex, ImageReaderFactory, Rect, autocenter

from .filesystem import scan_images
from .models import PlotForm, ScanForm
from .plotting.models import ImagePlotSpec
from .plotting.ports import PlotConfig, RawImagePlotter

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# TENG QUE PENSAR ALGO PARA ESTO ....
EXTENSIONS = (".fit", ".fits", ".fts", ".cr2")  # case-insensitive


def plot_image(
    path: str,
    form: PlotForm,
    factory: ImageReaderFactory,
    plotter: RawImagePlotter,
    config: PlotConfig,
) -> None:
    reader = factory.get_reader(path)
    metadata = reader.read_metadata(path)
    if form.x1 is None or form.y1 is None:
        section = autocenter(metadata.raw_width, metadata.raw_height, form.width, form.height)
    else:
        section = Rect(form.x1, form.y1, form.x1 + form.width, form.y1 + form.height)
    with reader.read_pixels(path) as pixels:
        red = pixels.red(None)
        green_r = pixels.greenr(None)
        blue = pixels.blue(None)
        green_b = pixels.greenb(None)
        red = ImagePlotSpec(
            bayer=BayerIndex.R,
            image=red,
            section=section,
            mean=np.mean(red),
            stddev=np.std(red),
            display_min=form.vmin,
            display_max=form.vmax,
        )
        green_r = ImagePlotSpec(
            bayer=BayerIndex.Gr,
            image=green_r,
            section=section,
            mean=np.mean(green_r),
            stddev=np.std(green_r),
            display_min=form.vmin,
            display_max=form.vmax,
        )
        blue = ImagePlotSpec(
            bayer=BayerIndex.B,
            image=blue,
            section=section,
            mean=np.mean(blue),
            stddev=np.std(blue),
            display_min=form.vmin,
            display_max=form.vmax,
        )
        green_b = ImagePlotSpec(
            bayer=BayerIndex.Gb,
            image=green_b,
            section=section,
            mean=np.mean(green_b),
            stddev=np.std(green_b),
            display_min=form.vmin,
            display_max=form.vmax,
        )
        data = (red, green_r, blue, green_b)
        plotter.plot(data, config, title=os.path.basename(path))


def batch_plot_images(
    scan: ScanForm,
    form: PlotForm,
    factory: ImageReaderFactory,
    plotter: RawImagePlotter,
    config: PlotConfig,
) -> None:
    paths = scan_images(scan.images_dir, scan.depth, EXTENSIONS)
    for path in paths:
        plot_image(path, form, factory, plotter, config)
