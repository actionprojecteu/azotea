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
    log.info("AZOTEA to be built .....")


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
