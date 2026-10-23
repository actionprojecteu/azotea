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
from lica_raw import BayerIndex, ImageReaderFactory, Rect, autocenter

from .models import PlotForm
from .plotting.models import ImagePlotSpec
from .plotting.ports import PlotConfig, RawImagePlotter

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


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
        section_red =  pixels.red(section)
        green_r = pixels.greenr(None)
        section_green_r = pixels.greenr(section)
        blue = pixels.blue(None)
        section_blue = pixels.blue(section)
        green_b = pixels.greenb(None)
        section_green_b = pixels.greenb(section)
        red = ImagePlotSpec(
            bayer=BayerIndex.R,
            image=red,
            image_mean=np.mean(red),
            image_stddev=np.std(red),
            image_min=form.vmin,
            image_max=form.vmax,
            image_sigmas_min=form.sigmas_min,
            image_sigmas_max=form.sigmas_max,
            section=section,
            section_mean=np.mean(section_red),
            section_stddev=np.std(section_red),
        )
        green_r = ImagePlotSpec(
            bayer=BayerIndex.Gr,
            image=green_r,
            image_mean=np.mean(green_r),
            image_stddev=np.std(green_r),
            image_min=form.vmin,
            image_max=form.vmax,
            image_sigmas_min=form.sigmas_min,
            image_sigmas_max=form.sigmas_max,
            section=section,
            section_mean=np.mean(section_green_r),
            section_stddev=np.std(section_green_r),
        )
        blue = ImagePlotSpec(
            bayer=BayerIndex.B,
            image=blue,
            image_mean=np.mean(blue),
            image_stddev=np.std(blue),
            image_min=form.vmin,
            image_max=form.vmax,
            image_sigmas_min=form.sigmas_min,
            image_sigmas_max=form.sigmas_max,
            section=section,
            section_mean=np.mean(section_blue),
            section_stddev=np.std(section_blue),
        )
        green_b = ImagePlotSpec(
            bayer=BayerIndex.Gb,
            image=green_b,
            image_mean=np.mean(green_b),
            image_stddev=np.std(green_b),
            image_min=form.vmin,
            image_max=form.vmax,
            image_sigmas_min=form.sigmas_min,
            image_sigmas_max=form.sigmas_max,
            section=section,
            section_mean=np.mean(section_green_b),
            section_stddev=np.std(section_green_b),
        )
        data = (red, green_r, blue, green_b)
        plotter.plot(data, config, title=os.path.basename(path))
