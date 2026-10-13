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

from azotea_cli import __version__
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.reader.adapters import ImageReaderFactoryImpl

# --------------
# local imports
# -------------
from azotea_cli.infra.sqlalchemy.noasync import engine
from azotea_cli.operation.adapters import SqaImagesRepo, SqaSkyBrightnessRepo
from azotea_cli.operation.models import RegisterForm
from azotea_cli.operation.use_cases import RegisterImagesUseCase, SkyStatisticsUseCase
from azotea_cli.provision.adapters import (
    SqaCameraRepo,
    SqaConsentRepo,
    SqaLocationRepo,
    SqaObserverRepo,
    SqaOpticsRepo,
    SqaRoiRepo,
)

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
    consent = SqaConsentRepo()
    camera = SqaCameraRepo()
    location = SqaLocationRepo()
    observer = SqaObserverRepo()
    optics = SqaOpticsRepo()
    roi = SqaRoiRepo()
    images = SqaImagesRepo()
    sky_stats = SqaSkyBrightnessRepo()
    factory = ImageReaderFactoryImpl()
    use_case1 = RegisterImagesUseCase(
        consent=consent,
        camera=camera,
        location=location,
        observer=observer,
        optics=optics,
        factory=factory,
        images=images,
    )
    use_case2 = SkyStatisticsUseCase(
        consent=consent,
        camera=camera,
        observer=observer,
        roi=roi,
        factory=factory,
        images=images,
        sky_stats=sky_stats,
    )
    form = RegisterForm(images_dir=args.images_dir, depth=args.depth)
    if args.only_load:
        use_case1.register_images(form)
    elif args.only_sky:
        use_case2.compute_sky_statistics()
    elif args.only_publish:
        raise NotImplementedError
    else:
        use_case1.register_images(form)
        use_case2.compute_sky_statistics()


def cli_main(args: Namespace) -> None:
    try:
        args.func(args)
    except AzoteaError as e:
        log.error(e)
        engine.dispose()


def main():
    """main entry point specified by pyproject.toml"""
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description=DESCRIPTION,
    )
