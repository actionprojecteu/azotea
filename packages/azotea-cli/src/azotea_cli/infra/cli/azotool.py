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

from azotea_cli import __version__
from azotea_cli.common.errors import AzoteaError
from azotea_cli.common.models import BayerPattern, HeaderType
from azotea_cli.common.reader.adapters import ImageReaderFactoryImpl
from azotea_cli.infra.cli.display import StdoutDisplay

# --------------
# local imports
# -------------
from azotea_cli.infra.sqlalchemy.noasync import engine
from azotea_cli.provision import (
    CameraForm,
    DefaultOpticsForm,
    LocationForm,
    ObserverForm,
    RoiCenteredForm,
    RoiForm,
)
from azotea_cli.provision.adapters import (
    SqaCameraRepo,
    SqaConsentRepo,
    SqaLocationRepo,
    SqaObserverRepo,
    SqaOpticsRepo,
    SqaRoiRepo,
)
from azotea_cli.provision.use_cases import (
    consent_view_and_agree,
    create_camera,
    create_camera_from_image,
    create_location,
    create_roi,
    create_roi_from_image,
    create_versioned_observer,
    save_default_optics,
    update_observer,
)
from azotea_cli.reports.adapters import (
    CsvExporterService,
    SqaReportsService,
    SqaSummaryService,
    TabDisplayService,
)
from azotea_cli.reports.use_cases import GenerateReportsUseCase, GenerateSummaryUseCase

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
    roicre.add_argument("--comment", type=str, default=None, help="Additional region comment")

    # ------------------------------------------
    # Create second level parsers for 'sky'
    # ------------------------------------------

    subparser = parser_sky.add_subparsers(dest="subcommand")

    skyexp = subparser.add_parser("export", help="Export to CSV")
    skyexp.set_defaults(func=cli_sky_export)
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
    skyview.set_defaults(func=cli_sky_summary)

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
    imgview.set_defaults(func=cli_img_summary)


def cli_consent(args: Namespace) -> None:
    consent = SqaConsentRepo()
    display = StdoutDisplay()
    consent_view_and_agree(consent, display, args.agree)


def cli_location(args: Namespace) -> None:
    location = SqaLocationRepo()
    consent = SqaConsentRepo()
    form = LocationForm(
        site_name=args.site_name,
        location=args.location,
        longitude=args.longitude,
        latitude=args.latitude,
        utc_offset=args.utc_offset,
    )
    create_location(location, consent, form, args.default)


def cli_optics(args: Namespace) -> None:
    optics = SqaOpticsRepo()
    consent = SqaConsentRepo()
    form = DefaultOpticsForm(
        focal_len=args.focal_length,
        f_number=args.f_number,
    )
    save_default_optics(optics, consent, form)


def cli_camera(args: Namespace) -> None:
    camera = SqaCameraRepo()
    consent = SqaConsentRepo()
    optics = SqaOpticsRepo()
    factory = ImageReaderFactoryImpl()
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
        create_camera(camera, consent, form, args.default)
    else:
        create_camera_from_image(camera, consent, optics, factory, args.from_image, args.default)


def cli_roi(args: Namespace) -> None:
    roi = SqaRoiRepo()
    factory = ImageReaderFactoryImpl()
    consent = SqaConsentRepo()
    optics = SqaOpticsRepo()

    if args.as_given:
        # El resto de valores deberia ser tambien requerido
        if args.x1 is None:
            raise AzoteaError("Camera model is required in --as-given")
        form = RoiForm(x1=args.x1, y1=args.y1, x2=args.x2, y2=args.y2, comment=args.comment)
        create_roi(roi, consent, form, args.default)
    else:
        form = RoiCenteredForm(width=args.width, height=args.height)
        create_roi_from_image(roi, consent, optics, factory, args.from_image, form, args.default)


def cli_observer(args: Namespace) -> None:
    observer = SqaObserverRepo()
    consent = SqaConsentRepo()
    form = ObserverForm(
        family_name=args.name,
        surname=args.surname,
        affiliation=args.affiliation,
        acronym=args.acronym,
    )
    if args.fix:
        update_observer(observer, consent, form)
    else:
        create_versioned_observer(observer, consent, form, args.default)


def cli_sky_export(args: Namespace) -> None:
    consent = SqaConsentRepo()
    reporter = SqaReportsService()
    observer = SqaObserverRepo()
    exporter = CsvExporterService(args.csv_dir)
    use_case = GenerateReportsUseCase(consent, observer, reporter, exporter)
    if args.all:
        use_case.generate_report_all()
    elif args.unpublished:
        use_case.generate_report_unpublished()
    elif args.range:
        use_case.generate_report_by_date_range(args.from_date, args.to_date)
    elif args.latest_night:
        use_case.generate_report_latest_night()
    elif args.latest_month:
        use_case.generate_report_latest_month()
    else:
        pass


def cli_sky_summary(args: Namespace) -> None:
    consent = SqaConsentRepo()
    observer = SqaObserverRepo()
    summarizer = SqaSummaryService()
    display = TabDisplayService()
    use_case = GenerateSummaryUseCase(consent, observer, summarizer, display)
    use_case.show_sky_summary()


def cli_img_summary(args: Namespace) -> None:
    consent = SqaConsentRepo()
    observer = SqaObserverRepo()
    summarizer = SqaSummaryService()
    display = TabDisplayService()
    use_case = GenerateSummaryUseCase(consent, observer, summarizer, display)
    use_case.show_image_summary()


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
        description="Database import",
    )
