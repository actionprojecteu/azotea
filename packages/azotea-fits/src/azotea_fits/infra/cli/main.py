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
from azotea_cli.common.errors import AzoteaError

from azotea_fits import __version__



# --------------
# local imports
# -------------


# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA FITS image preprocessor"

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
    pass




def cli_main(args: Namespace) -> None:
    try:
        args.func(args)
    except AzoteaError as e:
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
