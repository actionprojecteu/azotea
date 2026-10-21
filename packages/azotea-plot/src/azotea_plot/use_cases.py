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
from .plotting.models import RawImagePlotItem, RawImagePlotSet
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
        r_sigma = np.std(r)
        gr = pixels.greenr(None)
        gr_sigma = np.std(gr)
        b = pixels.blue(None)
        b_sigma = np.std(b)
        gb = pixels.greenb(None)
        gb_sigma = np.std(gb)
        data = RawImagePlotSet(
            red=RawImagePlotItem(channel=r, sigma=r_sigma * n_sigma),
            green_r=RawImagePlotItem(channel=gr, sigma=gr_sigma * n_sigma),
            green_b=RawImagePlotItem(channel=gb, sigma=gb_sigma * n_sigma),
            blue=RawImagePlotItem(channel=b, sigma=b_sigma * n_sigma),
        )
        plotter.plot(section, data, config)


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
