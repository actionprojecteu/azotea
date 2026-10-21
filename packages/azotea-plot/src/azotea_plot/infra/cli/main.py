# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
import logging
import sys
from argparse import ArgumentParser, Namespace

# from azotea_plot.models import FitsForm, ScanForm
# from azotea_plot.use_cases import plot_image, batch_plot_images
# -------------------
# Third party imports
# -------------------
from lica_cli import parse_args, run_cli
from lica_cli.validate import vdir, vfile
from lica_log.adapters.default import DefaultLogger
from lica_raw import Point, Rect
from lica_raw.adapters import ImageReaderFactoryImpl

# --------------
# local imports
# -------------
from azotea_plot import __version__
from azotea_plot.errors import AzoteaPlotError
from azotea_plot.models import Bounds, PlotForm, ScanForm
from azotea_plot.plotting.adapters.mock import MockPlotConfig, MockRawImagePlotter
from azotea_plot.use_cases import batch_plot_images, plot_image

# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA image Plotting utility"

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------
# Auxiliary functions
# -------------------


# -------------
# CLI Functions
# -------------


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command")
    iplot = subparser.add_parser("stats", help="Plot image stats / group of image stats")
    group = iplot.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d", "--images-dir", type=vdir, action="store", metavar="<path>", help="Images directory"
    )
    group.add_argument(
        "-f",
        "--image-file",
        type=vfile,
        action="store",
        metavar="<path>",
        help="single FITS file path",
    )
    iplot.add_argument(
        "-x", "--width", type=int, default=500, help="Region of interest width [pixels]."
    )
    iplot.add_argument(
        "-y", "--height", type=int, default=400, help="Region of interest height [pixels]."
    )
    iplot.add_argument("--x1", type=int, default=None, help="Region of interest X origin [pixels].")
    iplot.add_argument("--y1", type=int, default=None, help="Region of interest Y height [pixels].")
    iplot.add_argument("--vmin", type=int, default=None, help="minumim pixel value to display")
    iplot.add_argument("--vmax", type=int, default=None, help="maximum pixel value to display")
    iplot.add_argument(
        "--n-sigma", type=int, choices=range(1, 6), default=2, help="# of sigmas when autoscaling"
    )
    iplot.set_defaults(func=cli_plot)


def cli_plot(args: Namespace) -> None:
    factory = ImageReaderFactoryImpl()
    bounds = Bounds(low=args.vmin, high=args.vmax)
    form = PlotForm(
        n_sigma=args.n_sigma,
        x1=args.x1,
        y1=args.y1,
        width=args.width,
        height=args.height,
        bounds=bounds,
        title=None,
    )
    config = MockPlotConfig()
    plotter = MockRawImagePlotter()
    if args.images_dir:
        return
        scan = ScanForm(images_dir=args.images_dir, depth=args.dir_depth)
        batch_plot_image(scan, form, form, factory, plotter, config)
    else:
        plot_image(args.image_file, form, factory, plotter, config)


def cli_main(args: Namespace) -> None:
    try:
        args.func(args)
    except AzoteaPlotError as e:
        log.error(e)


def main():
    """main entry point specified by pyproject.toml"""
    args = parse_args(add_args, __name__, __version__, DESCRIPTION)
    logger = DefaultLogger(args)

    return_code = run_cli(cli_main, args, __name__, __version__, logger)
    sys.exit(return_code)
