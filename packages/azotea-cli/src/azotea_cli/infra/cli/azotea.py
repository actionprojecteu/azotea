# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import sys
import logging
from argparse import ArgumentParser, Namespace

# ---------------------
# Third party libraries
# ---------------------
from lica_cli import parse_args, run_cli
from lica_log.adapters.default import DefaultLogger
from lica_sqa.adapters.decouple import DcplDatabase
from lica_raw.adapters import ImageReaderFactoryImpl
from lica_tables.adapters.tabulate import StdoutDisplay

# ---------------
# Own dependecies
# ---------------
from azotea_cli import __version__
from azotea_cli.common.errors import AzoteaError, RepositoryError


from azotea_cli.operation.adapters import SqaImagesRepo, SqaSkyBrightnessRepo
from azotea_cli.operation.models import RegisterForm
from azotea_cli.operation.use_cases import ComputeSkyStatistics, RegisterImages
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
# create the database object
db = DcplDatabase("DATABASE_URL")

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
    consent = SqaConsentRepo(db)
    camera = SqaCameraRepo(db)
    location = SqaLocationRepo(db)
    observer = SqaObserverRepo(db)
    optics = SqaOpticsRepo(db)
    roi = SqaRoiRepo(db)
    images = SqaImagesRepo(db)
    sky_stats = SqaSkyBrightnessRepo(db)
    factory = ImageReaderFactoryImpl()
    use_case1 = RegisterImages(
        consent=consent,
        camera=camera,
        location=location,
        observer=observer,
        optics=optics,
        factory=factory,
        images=images,
    )
    use_case2 = ComputeSkyStatistics(
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
        use_case1.execute(form)
    elif args.only_sky:
        use_case2.execute()
    elif args.only_publish:
        raise NotImplementedError
    else:
        use_case1.execute(form)
        use_case2.execute()


def cli_main(args: Namespace) -> None:
    try:
        db.init()
        args.func(args)
    except RepositoryError as e:
        log.critical(e)
        StdoutDisplay().show(str(e))
    except AzoteaError as e:
        log.critical(e)
    finally:
        db.engine.dispose()


def main():
    """main entry point specified by pyproject.toml"""
    args = parse_args(add_args, __name__, __version__, DESCRIPTION)
    logger = DefaultLogger(args)

    return_code = run_cli(cli_main, args, __name__, __version__, logger)
    sys.exit(return_code)
