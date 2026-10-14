import logging
from datetime import datetime

from azotea_cli.provision.ports import (
    ConsentRepo,
    ObserverRepo,
)

from .ports import ExporterService, ReportsService

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class GenerateReportsUseCase:
    def __init__(
        self,
        consent: ConsentRepo,
        observer: ObserverRepo,
        reporter: ReportsService,
        exporter: ExporterService,
    ) -> None:
        self.consent = consent
        self.observer = observer
        self.reporter = reporter
        self.exporter = exporter

    def generate_report_all(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating complete report for %s %s", name, surname)
        data = self.reporter.get_all_data_by(observer_id)
        log.info("#" * 72)
        log.info(data)
        log.info("#" * 72)
        report_name = f"{surname}-all"
        self.exporter.export(report_name, data)

    def generate_report_unpublished(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating unpublised report for %s %s", name, surname)
        data = self.reporter.get_unpublished_data_by(observer_id)
        self.exporter.export(data)

    def generate_report_by_date_range(self, since: datetime, until: datetime) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating data range report for %s %s", name, surname)
        data = self.reporter.get_ranged_data_by(observer_id, since, until)
        self.exporter.export(data)


    def generate_report_latest_night(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating latest night report for %s %s", name, surname)
        data = self.reporter.get_latest_night_data_by(observer_id)
        self.exporter.export(data)

    def generate_report_latest_month(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating latest month report for %s %s", name, surname)
        data = self.reporter.get_latest_month_data_by(observer_id)
        self.exporter.export(data)
