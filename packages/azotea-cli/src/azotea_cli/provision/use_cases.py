import logging

from azotea_cli.common.reader.interfaces import ImageReaderFactory
from azotea_cli.common.rect import Point, Rect

from .interfaces import (
    CameraRepo,
    ConsentRepo,
    Display,
    LocationRepo,
    ObserverRepo,
    OpticsRepo,
    RoiRepo,
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


def consent_view_and_agree(consent: ConsentRepo, display: Display, agreed: bool) -> None:
    consent.review()
    display.display(consent.review())
    if agreed:
        consent.agree(agreed)


def consent_check(consent: ConsentRepo) -> None:
    consent.check_raises()


def create_location(
    location: LocationRepo, consent: ConsentRepo, form: LocationForm, as_default: bool
) -> None:
    consent.check_raises()
    loc_id = location.create(form)
    if as_default:
        location.set_default(loc_id)


def save_default_optics(optics: OpticsRepo, consent: ConsentRepo, form: DefaultOpticsForm) -> None:
    consent.check_raises()
    optics.save(form)


def load_default_optics(optics: OpticsRepo, consent: ConsentRepo) -> DefaultOptics:
    consent.check_raises()
    data = optics.load()
    return data


def create_versioned_observer(
    observer: ObserverRepo, consent: ConsentRepo, form: ObserverForm, as_default: bool
) -> None:
    consent.check_raises()
    obs_id = observer.create_versioned(form)
    if as_default:
        observer.set_default(obs_id)


def update_observer(observer: ObserverRepo, consent: ConsentRepo, form: ObserverForm) -> None:
    consent.check_raises()
    observer.update(form)


def create_camera(
    camera: CameraRepo, consent: ConsentRepo, form: CameraForm, as_default: bool
) -> None:
    consent.check_raises()
    cam_id = camera.create(form)
    if as_default:
        camera.set_default(cam_id)


def create_camera_from_image(
    camera: CameraRepo,
    consent: ConsentRepo,
    optics: OpticsRepo,
    factory: ImageReaderFactory,
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


def create_roi(roi: RoiRepo, consent: ConsentRepo, form: RoiForm, as_default: bool) -> None:
    consent.check_raises()
    roi_id = roi.create(form)
    if as_default:
        roi.set_default(roi_id)


def create_roi_from_image(
    roi: RoiRepo,
    consent: ConsentRepo,
    optics: OpticsRepo,
    factory: ImageReaderFactory,
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
