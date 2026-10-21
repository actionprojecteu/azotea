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

import numpy as np
from azotea_cli.common.filesystem import scan_images
from lica_raw import ImageMetadata, ImageReaderFactory, Point, Rect

from .models import PlotForm, ScanForm
from .plotting.models import ImagePlotSpec
from .plotting.ports import PlotConfig, RawImagePlotter

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# TENG QUE PENSAR ALGO PARA ESTO ....
EXTENSIONS = (".fit", ".fits", ".fts", ".cr2")  # case-insensitive


def autocenter(metadata: ImageMetadata, width: int, height: int) -> Rect:
    dim = Point(width, height) * 2  # to raw coordinates
    raw_size = Point(metadata.width, metadata.height)
    raw_screen = Rect.from_points(Point.zero(), raw_size)
    rect = Rect.from_points(Point.zero(), dim).recenter_on(raw_screen)
    rect = rect // 2  # to each plane coordinates
    return rect


def plot_image(
    path: str,
    form: PlotForm,
    factory: ImageReaderFactory,
    plotter: RawImagePlotter,
    config: PlotConfig,
) -> None:
    reader = factory.get_reader(path)
    n_sigma = form.n_sigma
    metadata = reader.read_metadata(path)
    if form.x1 is None or form.y1 is None:
        section = autocenter(metadata, form.width, form.height)
    else:
        section = Rect(form.x1, form.y1, form.x1 + form.width, form.y1 + form.height)

    with reader.read_pixels(path) as pixels:
        r = pixels.red(None)
        gr = pixels.greenr(None)
        b = pixels.blue(None)
        gb = pixels.greenb(None)
        red = ImagePlotSpec(title="R", image=r, section=section, mean=np.mean(r), stddev=np.std(r),display_min=form.vmin, display_max=form.vmax)
        green_r = ImagePlotSpec(title="Gr", image=gr, section=section, mean=np.mean(gr), stddev=np.std(gr),display_min=form.vmin, display_max=form.vmax)
        blue = ImagePlotSpec(title="B", image=b, section=section, mean=np.mean(b), stddev=np.std(b),display_min=form.vmin, display_max=form.vmax)
        green_b = ImagePlotSpec(title="Gb", image=gb, section=section, mean=np.mean(gb), stddev=np.std(gb),display_min=form.vmin, display_max=form.vmax)
        data = (red, green_r, blue, green_b)
        plotter.plot(data, config)


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
