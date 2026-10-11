from azotea_cli.common.reader import ImageReaderFactory
from azotea_cli.provision.interfaces import (
    CameraRepo,
    ConsentRepo,
    LocationRepo,
    ObserverRepo,
    RoiRepo,
)


class SkyStatisticsUseCase:
    def __init__(
        self,
        consent: ConsentRepo,
        camera: CameraRepo,
        location: LocationRepo,
        observer: ObserverRepo,
        roi: RoiRepo,
        factory: ImageReaderFactory,
    ) -> None:
        self.consent = consent
        self.camera = camera
        self.location = location
        self.observer = observer
        self.roi = roi
        self.factory = factory

    def compute_sky_statistics(self) -> None:
        self.consent.check_raises()
