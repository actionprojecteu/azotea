# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
#
import logging
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------
from lica.cli import execute

# --------------
# local imports
# -------------

from azotea_cli import __version__
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.reader.adapters import ImageReaderFactoryImpl

from azotea_cli.provision.adapters import (
    CameraRepoImpl,
    ConsentRepoImpl,
    LocationRepoImpl,
    ObserverRepoImpl,
    OpticsRepoImpl,
    RoiRepoImpl,
)

from azotea_cli.operation.adapters import ImagesRepoImpl, SkyBrightnessRepoImpl
from azotea_cli.operation.use_cases import RegisterImagesUseCase, SkyStatisticsUseCase
from azotea_cli.operation.models import RegisterForm

# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA image processing tool"

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

    # --------------------------
    # Create first level parsers
    # --------------------------

    subparser = parser.add_subparsers(dest="command")
    parser_batch = subparser.add_parser("batch", help="observer commands")
    parser_batch.set_defaults(func=cli_batch)

    # -----------------------------
    # Arguments for 'batch' command
    # -----------------------------

    parser_batch.add_argument(
        "--images-dir",
        type=str,
        default=None,
        action="store",
        metavar="<path>",
        help="Images working directory",
    )
    parser_batch.add_argument(
        "--depth", type=int, default=None, help="Specify images dir max. scanning depth"
    )
    group = parser_batch.add_mutually_exclusive_group()
    group.add_argument("--only-sky", action="store_true", help="only compute sky background")
    group.add_argument("--only-load", action="store_true", help="only loads images to database")
    group.add_argument("--only-publish", action="store_true", help="only publish to server")
    # only makes sense after image background computation
    parser_batch.add_argument("--publish", action="store_true", help="optionally publish to server")
    parser_batch.set_defaults(func=cli_batch)


def cli_batch(args: Namespace) -> None:
    consent = ConsentRepoImpl()
    camera = CameraRepoImpl()
    location = LocationRepoImpl()
    observer = ObserverRepoImpl()
    optics = OpticsRepoImpl()
    roi = RoiRepoImpl()
    images = ImagesRepoImpl()
    sky_stats = SkyBrightnessRepoImpl()
    factory = ImageReaderFactoryImpl()
    use_case1 = RegisterImagesUseCase(
        consent = consent,
        camera = camera,
        location = location,
        observer = observer,
        optics = optics,
        factory = factory,
        images = images,
    )
    use_case2 = SkyStatisticsUseCase(
        consent = consent,
        camera = camera,
        observer = observer,
        roi = roi,
        factory = factory,
        images = images,
        sky_stats = sky_stats
    )
    form = RegisterForm(images_dir=args.images_dir, depth=args.depth)
    try:
        if args.only_load:
            use_case1.register_images(form)
        elif args.only_sky:
            use_case2.compute_sky_statistics()
        elif args.only_publish:
            raise NotImplementedError
        else:
            use_case1.register_images(form)
            use_case2.compute_sky_statistics()
    except AzoteaError as e:
        log.error(e)


def cli_main(args: Namespace) -> None:
    args.func(args)


def main():
    """main entry point specified by pyproject.toml"""
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description=DESCRIPTION,
    )
