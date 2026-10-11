import logging

from azotea_cli.common.reader.interfaces import ReaderFactory
from azotea_cli.common.rect import Point, Rect

from .interfaces import (
    CameraProv,
    ConsentProv,
    Display,
    LocationProv,
    ObserverProv,
    OpticsProv,
    RoiProv,
)
from .models import (
    CameraForm,
    DefaultOptics,
    DefaultOpticsForm,
    LocationForm,
    ObserverForm,
    RoiCenteredForm,
    RoiForm,
)

log = logging.getLogger(__name__.split(".")[-2])


def consent_view_and_agree(consent: ConsentProv, display: Display, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)


def consent_check(consent: ConsentProv) -> None:
    consent.check_raises()


def create_location(
    location: LocationProv, consent: ConsentProv, form: LocationForm, as_default: bool
) -> None:
    consent.check_raises()
    loc_id = location.create(form)
    if as_default:
        location.set_default(loc_id)


def save_default_optics(optics: OpticsProv, consent: ConsentProv, form: DefaultOpticsForm) -> None:
    consent.check_raises()
    optics.save(form)


def load_default_optics(optics: OpticsProv, consent: ConsentProv) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    return data


def create_versioned_observer(
    observer: ObserverProv, consent: ConsentProv, form: ObserverForm, as_default: bool
) -> None:
    consent.check_raises()
    obs_id = observer.create_versioned(form)
    if as_default:
        observer.set_default(obs_id)


def update_observer(observer: ObserverProv, consent: ConsentProv, form: ObserverForm) -> None:
    consent.check_raises()
    observer.update(form)


def create_camera(
    camera: CameraProv, consent: ConsentProv, form: CameraForm, as_default: bool
) -> None:
    consent.check_raises()
    cam_id = camera.create(form)
    if as_default:
        camera.set_default(cam_id)


def create_camera_from_image(
    camera: CameraProv,
    consent: ConsentProv,
    optics: OpticsProv,
    factory: ReaderFactory,
    path: str,
    as_default: bool,
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    reader = factory.get_reader(path)
    metadata = reader.read_metadata(path, default_optics.focal_len, default_optics.f_number)
    cam_id = camera.create_from_image(metadata)
    if as_default:
        camera.set_default(cam_id)


def create_roi(roi: RoiProv, consent: ConsentProv, form: RoiForm, as_default: bool) -> None:
    consent.check_raises()
    roi_id = roi.create(form)
    if as_default:
        roi.set_default(roi_id)


def create_roi_from_image(
    roi: RoiProv,
    consent: ConsentProv,
    optics: OpticsProv,
    factory: ReaderFactory,
    path: str,
    form: RoiCenteredForm,
    as_default: bool,
) -> None:
    consent.check_raises()
    default_optics = optics.load()
    reader = factory.get_reader(path)
    metadata = reader.read_metadata(path, default_optics.focal_len, default_optics.f_number)
    dim = Point(form.width, form.height) * 2  # to raw coordinates
    raw_size = Point(metadata.width, metadata.height)
    raw_screen = Rect.from_points(Point.zero(), raw_size)
    rect = Rect.from_points(Point.zero(), dim).recenter_on(raw_screen)
    rect = rect // 2  # to each plane coordinates
    roi_id = roi.create_from_image(rect, metadata)
    if as_default:
        roi.set_default(roi_id)
