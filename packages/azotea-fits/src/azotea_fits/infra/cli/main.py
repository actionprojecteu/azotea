# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
#
import logging
from argparse import ArgumentParser, Namespace

# --------------
# local imports
# -------------
from azotea_cli.common.types import BayerPattern, ImageType

# -------------------
# Third party imports
# -------------------
from lica.cli import execute
from lica.validators import vdate, vdir, vfile

#
from azotea_fits import __version__
from azotea_fits.adapters.factory import EditorFactoryImpl
from azotea_fits.enums import SwCreator
from azotea_fits.errors import AzoteaFitsError
from azotea_fits.models import FitsForm, ScanForm
from azotea_fits.use_cases import edit_fits_file, edit_fits_files

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
    parser_edit = subparser.add_parser("edit", help="consent command")
    parser_creator = subparser.add_parser("creator", help="observer commands")

    # --------------------------------------
    # Create second level parsers for 'edit'
    # --------------------------------------

    parser_edit.set_defaults(func=cli_edit)
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
        "--swcreator",
        choices=SwCreator,
        default=None,
        action="store",
        help="Name of software that created the FITS files",
    )
    parser_creator.set_defaults(func=cli_sw_creator)


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
        edit_fits_files(scan, form, factory)
    else:
        edit_fits_file(args.image_file, form, factory)


def cli_sw_creator(args: Namespace) -> None:
    pass


def cli_main(args: Namespace) -> None:
    try:
        args.func(args)
    except AzoteaFitsError as e:
        log.error(e)


def main():
    """main entry point specified by pyproject.toml"""
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description=DESCRIPTION,
    )
