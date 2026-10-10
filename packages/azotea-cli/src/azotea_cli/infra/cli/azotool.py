# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------
from lica.cli import execute
from lica.validators import vdate, vfile

# --------------
# local imports
# -------------
from azotea_cli import __version__
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.enums import BayerPattern, HeaderType
from azotea_cli.provision import CameraForm, LocationForm, ObserverForm, RoiForm, DefaultOpticsForm
from azotea_cli.provision.use_cases import consent_view_and_agree
from azotea_cli.provision.adapters import ConsentProvImpl
from azotea_cli.infra.cli.display import StdoutDisplay

# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA provision tool"

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

    parser_consent = subparser.add_parser("consent", help="consent command")
    parser_observer = subparser.add_parser("observer", help="observer commands")
    parser_location = subparser.add_parser("location", help="location commands")
    parser_camera = subparser.add_parser("camera", help="camera commands")
    parser_roi = subparser.add_parser("roi", help="roi commands")
    parser_misc = subparser.add_parser("configure", help="miscelanea commands")
    parser_sky = subparser.add_parser("sky", help="sky background commands")
    parser_img = subparser.add_parser("image", help="images commands")

    # -----------------------------------------
    # Create second level parsers for 'consent'
    # -----------------------------------------

    subparser = parser_consent.add_subparsers(dest="subcommand")

    conform = subparser.add_parser("view", help="View consent form")
    conform.add_argument("--agree", action="store_true", help="Auto-agree conset form")
    conform.set_defaults(func=cli_consent)

    # ------------------------------------------
    # Create second level parsers for 'observer'
    # ------------------------------------------

    subparser = parser_observer.add_subparsers(dest="subcommand")

    obscre = subparser.add_parser("create", help="Create a new observer in the database")
    obscre.add_argument(
        "--default", action="store_true", help="Set this observer as the default observer"
    )
    obscre.add_argument("--name", type=str, required=True, help="Observer's name")
    obscre.add_argument("--surname", type=str, required=True, help="Observer's surname")
    obscre.add_argument("--affiliation", type=str, default=None, help="Complete affiliation name")
    obscre.add_argument("--acronym", type=str, default=None, help="Affiliation acronym")
    obscre.add_argument(
        "--fix", action="store_true", help="Fix only affiliation/acronym (advance use)"
    )
    obscre.set_defaults(func=cli_observer)

    # ------------------------------------------
    # Create second level parsers for 'location'
    # ------------------------------------------

    subparser = parser_location.add_subparsers(dest="subcommand")

    loccre = subparser.add_parser("create", help="Create a new location in the database")
    loccre.add_argument(
        "--default", action="store_true", help="Set this location as the default location"
    )
    loccre.add_argument("--site-name", type=str, required=True, help="Name identifying the place")
    loccre.add_argument(
        "--location", type=str, required=True, help="City/Town where the site belongs to"
    )
    loccre.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Site longitude in decimal degrees, negative West",
    )
    loccre.add_argument(
        "--latitude",
        type=float,
        default=None,
        help="Site latitude in decimal degrees, negative South",
    )
    loccre.add_argument(
        "--utc-offset",
        type=int,
        default=None,
        help="**CAMERA UTC offset!** (if not set in UTC) GMT+1 = +1 ",
    )
    loccre.add_argument(
        "--randomize",
        action="store_true",
        default=None,
        help="randomize a bit the geographical coordinates",
    )
    loccre.set_defaults(func=cli_location)

    # ----------------------------------------
    # Create second level parsers for 'camera'
    # ----------------------------------------

    subparser = parser_camera.add_subparsers(dest="subcommand")

    camcre = subparser.add_parser("create", help="Create a new camera in the database")
    camcre.set_defaults(func=cli_camera)

    camcre.add_argument(
        "--default", action="store_true", help="Set this camera as the default camera"
    )
    group = camcre.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--from-image",
        type=vfile,
        default=None,
        action="store",
        metavar="<image file path>",
        help="create camera by inspecting an image",
    )
    group.add_argument(
        "--as-given", action="store_true", help="create camera by adding further parameters"
    )
    # additional argumnets with the --as-given option
    camcre.add_argument(
        "--model", type=str, default=None, help="Camera Model (taken from EXIF data)"
    )
    camcre.add_argument(
        "--bias",
        type=int,
        default=None,
        help="default bias, to be replicated in all channels if we cannot read ir from EXIF",
    )
    camcre.add_argument(
        "--extension",
        type=str,
        default=None,
        help="File extension produced by a camera (i.e. .NEF)",
    )
    camcre.add_argument(
        "--header-type", choices=HeaderType, default=None, help="Either 'EXIF' or 'FITS'"
    )
    camcre.add_argument(
        "--bayer-pattern", choices=BayerPattern, default=None, help="Bayer pattern grid"
    )
    camcre.add_argument(
        "--width", type=int, default=None, help="Number of raw columns, with no debayering"
    )
    camcre.add_argument(
        "--height", type=int, default=None, help="Number of raw rows, with no debayering"
    )
    camcre.add_argument("--x-pixsize", type=float, default=None, help="Pixel width in um.")
    camcre.add_argument("--y-pixsize", type=float, default=None, help="Pixel height in um.")

    camswi = subparser.add_parser(
        "switch", help="Switch default camera to an existing model in the database"
    )
    # This si none bty default becaiuse of the exclusev group (--as-given | --from-image)
    camswi.add_argument(
        "--model", type=str, default=None, help="Camera Model (taken from EXIF data)"
    )

    # -------------------------------------
    # Create second level parsers for 'roi'
    # -------------------------------------

    subparser = parser_roi.add_subparsers(dest="subcommand")

    roicre = subparser.add_parser("create", help="Create a new region of interest in the database")
    roicre.set_defaults(func=cli_roi)
    roiswi = subparser.add_parser(
        "switch",
        help="Switch default ROI to the auto centered ROI for the given camera and width and height",
    )

    group = roicre.add_mutually_exclusive_group(required=True)
    roicre.add_argument("--default", action="store_true", help="Set this ROI as the default ROI")
    group.add_argument(
        "--from-image",
        type=str,
        default=None,
        action="store",
        metavar="<image file path>",
        help="create camera by inspecting an image",
    )
    group.add_argument(
        "--as-given", action="store_true", help="create camera by adding further parameters"
    )
    # additional argumnets with the --from-image option
    roicre.add_argument("--width", type=int, default=None, help="Width of central rectangle")
    roicre.add_argument("--height", type=int, default=None, help="height of central rectangle")
    # additional argumnets with the --as-given option
    roicre.add_argument("--x1", type=int, default=None, help="Starting pixel column")
    roicre.add_argument("--y1", type=int, default=None, help="Starting pixel row")
    roicre.add_argument("--x2", type=int, default=None, help="Ending pixel column")
    roicre.add_argument("--y2", type=int, default=None, help="Ending pixel row")
    roicre.add_argument(
        "--comment", type=str, default=None, help="Additional region comment"
    )

    roiswi.add_argument(
        "--model", type=str, default=None, help="Camera Model (taken from EXIF data)"
    )
    roiswi.add_argument("--width", type=int, default=500, help="Width of central rectangle")
    roiswi.add_argument("--height", type=int, default=400, help="height of central rectangle")

    # ------------------------------------------
    # Create second level parsers for 'sky'
    # ------------------------------------------

    subparser = parser_sky.add_subparsers(dest="subcommand")

    skyexp = subparser.add_parser("export", help="Export to CSV")
    skyexp.add_argument(
        "--csv-dir",
        type=str,
        required=True,
        action="store",
        metavar="<csv directory>",
        help="directory where to place CSV files",
    )
    group = skyexp.add_mutually_exclusive_group(required=True)
    group.add_argument("--latest-month", action="store_true", help="Latest month in database")
    group.add_argument("--latest-night", action="store_true", help="Latest night in database")
    group.add_argument("--all", action="store_true", help="Export all nights")
    group.add_argument(
        "--unpublished", action="store_true", help="Export observations not yet published to server"
    )
    group.add_argument("--range", action="store_true", help="Export a date range")
    # options for range export
    skyexp.add_argument(
        "--from-date", type=vdate, default=None, metavar="<YYYY-MM-DD>", help="Start date in range"
    )
    skyexp.add_argument(
        "--to-date", type=vdate, default=None, metavar="<YYYY-MM-DD>", help="End date in range"
    )

    skyview = subparser.add_parser("summary", help="view sky summary data")

    # --------------------------------------------
    # Create second level parsers for 'configure'
    # --------------------------------------------

    subparser = parser_misc.add_subparsers(dest="subcommand")

    miscopt = subparser.add_parser(
        "optics", help="Create the 'optics' section in the configuration"
    )
    miscopt.set_defaults(func=cli_optics)
    miscopt.add_argument(
        "--focal-length", type=float, required=True, help="Camera focal length in mm."
    )
    miscopt.add_argument("--f-number", type=float, required=True, help="Camera f/ ratio")

    pubcre = subparser.add_parser(
        "publishing", help="create the 'publishing' section in the configuration"
    )
    pubcre.add_argument("--username", type=str, required=True, help="Server username")
    pubcre.add_argument("--password", type=str, required=True, help="Server password")
    pubcre.add_argument("--url", type=str, required=True, help="Server URL")

    # ---------------------------------------
    # Create second level parsers for 'image'
    # ---------------------------------------

    subparser = parser_img.add_subparsers(dest="subcommand")
    imgview = subparser.add_parser("summary", help="View image summary data")


def cli_consent(args: Namespace) -> None:
    consent = ConsentProvImpl()
    display = StdoutDisplay()
    consent_view_and_agree(consent, display, args.agree)


def cli_location(args: Namespace) -> None:
    prov = Provision()
    form = LocationForm(
        site_name=args.site_name,
        location=args.location,
        longitude=args.longitude,
        latitude=args.latitude,
        utc_offset=args.utc_offset,
    )
    try:
        prov.create_location(form, args.default)
    except AzoteaError as e:
        log.error(e)

def cli_optics(args: Namespace) -> None:
    prov = Provision()
    form = DefaultOpticsForm(
        focal_len=args.focal_length,
        f_number=args.f_number,
    )
    try:
        prov.save_default_optics(form)
    except AzoteaError as e:
        log.error(e)

def cli_camera(args: Namespace) -> None:
    prov = Provision()
    if args.as_given:
        # El resto de valores deberia ser tambien requerido
        if args.model is None:
            raise AzoteaError("Camera model is required in --as-given")

        form = CameraForm(
            model=args.model,
            bayer_pattern=args.bayer_pattern,
            header_type=args.header_type,
            extension=args.extension,
            width=args.width,
            height=args.height,
            bias=args.bias,
            x_pixsize=args.x_pixsize,
            y_pixsize=args.y_pixsize,
        )
        try:
            prov.create_camera(form, args.default)
        except AzoteaError as e:
            log.error(e)

    else:
        try:
            prov.create_camera_from_image(args.from_image, args.default)
        except AzoteaError as e:
            log.error(e)


def cli_roi(args: Namespace) -> None:
    prov = Provision()
    if args.as_given:
        # El resto de valores deberia ser tambien requerido
        if args.x1 is None:
            raise AzoteaError("Camera model is required in --as-given")
        form = RoiForm(
            x1=args.x1,
            y1=args.y1,
            x2=args.x2,
            y2=args.y2,
            comment = args.comment
        )
        try:
            prov.create_roi(form, args.default)
        except AzoteaError as e:
            log.error(e)

    else:
        try:
            prov.create_roi_from_image(args.from_image, args.width, args.height, args.default)
        except AzoteaError as e:
            log.error(e)


def cli_observer(args: Namespace) -> None:
    prov = Provision()
    form = ObserverForm(
        family_name=args.name,
        surname=args.surname,
        affiliation=args.affiliation,
        acronym=args.acronym,
    )
    try:
        if args.fix:
            prov.update_observer(form)
        else:
            prov.create_observer_vers(form, args.default)
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
        description="Database import",
    )
