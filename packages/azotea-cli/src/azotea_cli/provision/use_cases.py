# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging
import os

from lica_tables import DisplayService
from lica_raw import ImageMetadata, ImageReaderFactory, Point, Rect, autocenter
# ----------------
# Own dependencies
# ----------------

from .errors import (
    MissingBlackLevelError,
    MissingCameraModelError,
    MissingDateObsError,
    MissingExpTimeError,
    MissingIsoOrGainError,
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
from .ports import (
    CameraRepo,
    ConsentService,
    LocationRepo,
    ObserverRepo,
    OpticsRepo,
    RoiRepo,
)

log = logging.getLogger(__name__.split(".")[-2])


def consent_view_and_agree(consent: ConsentService, display: DisplayService, agreed: bool) -> None:
    consent.review()
    display.show(consent.review())
    if agreed:
        consent.agree(agreed)


class CreateLocation:
    def __init__(self, location: LocationRepo, consent: ConsentService) -> None:
        self.location = location
        self.consent = consent

    def execute(self, form: LocationForm, as_default: bool) -> None:
        self.consent.check_raises()
        loc_id = self.location.create(form)
        if as_default:
            self.location.set_default(loc_id)


class SaveDefaultOptics:
    def __init__(self, optics: OpticsRepo, consent: ConsentService) -> None:
        self.optics = optics
        self.consent = consent

    def execute(self, form: DefaultOpticsForm) -> None:
        self.consent.check_raises()
        self.optics.save(form)


class LoadDefaultOptics:
    def __init__(self, optics: OpticsRepo, consent: ConsentService) -> None:
        self.optics = optics
        self.consent = consent

    def execute(self, form: DefaultOpticsForm) -> DefaultOptics:
        self.consent.check_raises()
        return self.optics.load()


class CreateVersionedObserver:
    def __init__(self, observer: ObserverRepo, consent: ConsentService) -> None:
        self.observer = observer
        self.consent = consent

    def execute(self, form: ObserverForm, as_default: bool) -> None:
        self.consent.check_raises()
        obs_id = self.observer.create_versioned(form)
        if as_default:
            self.observer.set_default(obs_id)


class UpdateObserver:
    def __init__(self, observer: ObserverRepo, consent: ConsentService) -> None:
        self.observer = observer
        self.consent = consent

    def execute(self, form: ObserverForm) -> None:
        self.consent.check_raises()
        self.observer.update(form)


class CreateCamera:
    def __init__(self, camera: CameraRepo, consent: ConsentService) -> None:
        self.camera = camera
        self.consent = consent

    def execute(self, form: CameraForm, as_default: bool) -> None:
        self.consent.check_raises()
        cam_id = self.camera.create(form)
        if as_default:
            self.camera.set_default(cam_id)


class CreateCameraFromImage:
    def __init__(
        self,
        camera: CameraRepo,
        consent: ConsentService,
        optics: OpticsRepo,
        factory: ImageReaderFactory,
    ) -> None:
        self.camera = camera
        self.consent = consent
        self.optics = optics
        self.factory = factory

    def validate(self, m: ImageMetadata, path: str, default_optics: DefaultOptics) -> None:
        if m.model is None:
            raise MissingCameraModelError(f"{os.path.basename(path)}")
        if m.exptime is None:
            raise MissingExpTimeError(f"{os.path.basename(path)}")
        if m.iso is None and m.gain is None:
            raise MissingIsoOrGainError(f"{os.path.basename(path)}")
        if m.black_level is None:
            raise MissingBlackLevelError(f"{os.path.basename(path)}")
        if m.timestamp is None:
            raise MissingDateObsError(os.path.basename(path))
        m.focal_len = default_optics.focal_len if m.focal_len is None else m.focal_len
        m.f_number = default_optics.f_number if m.f_number is None else m.f_number

    def execute(self, path: str, as_default: bool) -> None:
        self.consent.check_raises()
        default_optics = self.optics.load()
        reader = self.factory.get_reader(path)
        metadata = reader.read_metadata(path)
        self.validate(metadata, path, default_optics)
        cam_id = self.camera.create_from_image(metadata)
        if as_default:
            self.camera.set_default(cam_id)


class CreateRoi:
    def __init__(self, roi: RoiRepo, consent: ConsentService) -> None:
        self.roi = roi
        self.consent = consent

    def execute(self, form: RoiForm, as_default: bool) -> None:
        self.consent.check_raises()
        roi_id = self.roi.create(form)
        if as_default:
            self.roi.set_default(roi_id)


class CreateRoiFromImage:
    def __init__(self, roi: RoiRepo, consent: ConsentService, factory: ImageReaderFactory) -> None:
        self.roi = roi
        self.consent = consent
        self.factory = factory

    def execute(self, path: str, form: RoiCenteredForm, as_default: bool) -> None:
        self.consent.check_raises()
        reader = self.factory.get_reader(path)
        metadata = reader.read_metadata(path)
        rect = autocenter(metadata.raw_width, metadata.raw_height, form.width, form.height)
        roi_id = self.roi.create_from_image(rect, metadata)
        if as_default:
            self.roi.set_default(roi_id)
