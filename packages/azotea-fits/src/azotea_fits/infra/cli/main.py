# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
import logging
import sys
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------
from lica_cli import parse_args, run_cli
from lica_cli.validate import vdate, vdir, vfile
from lica_log.adapters.default import DefaultLogger
from lica_raw import BayerPattern, ImageType
from lica_tables.adapters.tabulate import StdoutDisplay

# --------------
# local imports
# -------------
from azotea_fits import __version__
from azotea_fits.adapters.factory import EditorFactoryImpl
from azotea_fits.enums import SwCreator
from azotea_fits.errors import AzoteaFitsError
from azotea_fits.models import FitsForm, ScanForm
from azotea_fits.use_cases import (
    batch_edit_fits,
    batch_set_software_creator,
    batch_show_fits_metadata,
    edit_fits,
    set_software_creator,
    show_fits_metadata,
)

# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA FITS image pre-processor"

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
    parser.add_argument(
        "--dir-depth",
        type=int,
        default=8,
        help="Images directory depth, 8 by default, 0=scan only base directory",
    )
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument(
        "-d",
        "--images-dir",
        type=vdir,
        action="store",
        metavar="<path>",
        help="Base directory to edit FITS files",
    )
    group1.add_argument(
        "-f",
        "--image-file",
        type=vfile,
        action="store",
        metavar="<path>",
        help="single FITS file path",
    )

    # --------------------------
    # Create first level parsers
    # --------------------------

    subparser = parser.add_subparsers(dest="command")
    parser_edit = subparser.add_parser("edit", help="edit command")
    parser_edit.set_defaults(func=cli_edit)
    parser_creator = subparser.add_parser("creator", help="sw creator commands")
    parser_creator.set_defaults(func=cli_sw_creator)
    parser_view = subparser.add_parser("view", help="view metadata command")
    parser_view.set_defaults(func=cli_view)

    # --------------------------------------
    # Create second level parsers for 'edit'
    # --------------------------------------

    parser_edit.add_argument("--camera", type=str, default=None, help="Camera model")
    parser_edit.add_argument(
        "--comment", type=str, default=None, help="Optional comment keyword to add"
    )
    parser_edit.add_argument(
        "--bayer-pattern", choices=BayerPattern, default=None, help="Bayer pattern layout"
    )
    parser_edit.add_argument("--gain", type=float, default=None, help="CMOS detector GAIN settings")
    parser_edit.add_argument("--bias", type=int, default=None, help="Global Bias for every image")
    parser_edit.add_argument("--x-pixsize", type=float, default=None, help="Pixel width in um.")
    parser_edit.add_argument("--y-pixsize", type=float, default=None, help="Pixel height in um.")
    parser_edit.add_argument("--image-type", choices=ImageType, default=None, help="Image type")
    parser_edit.add_argument("--diameter", type=float, default=None, help="Optics diameter in mm.")
    parser_edit.add_argument("--focal-length", type=float, default=None, help="Focal length in mm.")
    parser_edit.add_argument(
        "--date-obs",
        type=vdate,
        default=None,
        metavar="<YYYY-MM-DDTHH:MM:SS>",
        help="UTC Observation date.",
    )
    parser_edit.add_argument("--exptime", type=float, default=None, help="Exposure time in sec.")

    # FITS specific editing info
    parser_creator.add_argument(
        "--set",
        choices=SwCreator,
        default=None,
        action="store",
        help="Set the name of software that created the FITS files",
    )


def cli_edit(args: Namespace) -> None:
    factory = EditorFactoryImpl()
    form = FitsForm(
        camera=args.camera,
        bayer_pattern=args.bayer_pattern,
        gain=args.gain,
        bias=args.bias,
        x_pixsize=args.x_pixsize,
        y_pixsize=args.y_pixsize,
        image_type=args.image_type,
        diameter=args.diameter,
        focal_length=args.focal_length,
        date_obs=args.date_obs,
        exptime=args.exptime,
    )
    if args.images_dir:
        scan = ScanForm(images_dir=args.images_dir, depth=args.dir_depth)
        batch_edit_fits(scan, form, factory)
    else:
        edit_fits(args.image_file, form, factory)


def cli_sw_creator(args: Namespace) -> None:
    factory = EditorFactoryImpl()
    if args.images_dir:
        scan = ScanForm(images_dir=args.images_dir, depth=args.dir_depth)
        batch_set_software_creator(scan, args.set, factory)
    else:
        set_software_creator(args.image_file, args.set, factory)


def cli_view(args: Namespace) -> None:
    factory = EditorFactoryImpl()
    display = StdoutDisplay(table_fmt="presto")
    if args.images_dir:
        scan = ScanForm(images_dir=args.images_dir, depth=args.dir_depth)
        batch_show_fits_metadata(scan, factory, display)
    else:
        show_fits_metadata(args.image_file, factory, display)


def cli_main(args: Namespace) -> None:
    try:
        args.func(args)
    except AzoteaFitsError as e:
        log.error(e)


def main():
    """main entry point specified by pyproject.toml"""
    args = parse_args(add_args, __name__, __version__, DESCRIPTION)
    logger = DefaultLogger(args)

    return_code = run_cli(cli_main, args, __name__, __version__, logger)
    sys.exit(return_code)
