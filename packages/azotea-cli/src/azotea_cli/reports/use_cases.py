import logging
from datetime import datetime

from azotea_cli.provision.ports import (
    ConsentService,
    ObserverRepo,
)

from azotea_cli.common.ports import DisplayService
from .ports import ExporterService, ReportsService, SummaryService

# -----------------------
# Module global variables
# -----------------------

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class GenerateReportsUseCase:
    def __init__(
        self,
        consent: ConsentService,
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
        data = self.reporter.get_all_data_by(observer_id)
        report_name = f"{surname}-all"
        length = len(data)
        if length:
            log.info("generating '%s' report for '%s %s' (%d rows)", report_name,  name, surname, length)
            self.exporter.export(report_name, data)
        else:
            log.warning("No data to export")

    def generate_report_unpublished(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        data = self.reporter.get_unpublished_data_by(observer_id)
        report_name = f"{surname}-unpublished"
        length = len(data)
        if length:
            log.info("generating '%s' report for '%s %s' (%d rows)", report_name,  name, surname, length)
            self.exporter.export(report_name, data)
        else:
            log.warning("No data to export")

    def generate_report_by_date_range(self, since: datetime, until: datetime) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        data = self.reporter.get_ranged_data_by(observer_id, since, until)
        report_name = f"{surname}-since-{since.strftime("%Y%m%d")}-until-{until.strftime("%Y%m%d")}"
        length = len(data)
        if length:
            log.info("generating '%s' report for '%s %s' (%d rows)", report_name,  name, surname, length)
            self.exporter.export(report_name, data)
        else:
            log.warning("No data to export")

    def generate_report_latest_night(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        log.info("generating latest night report for '%s %s'", name, surname)
        data, latest_day = self.reporter.get_latest_night_data_by(observer_id)
        report_name = f"{surname}-{latest_day.strftime("%Y%m%d")}"
        length = len(data)
        if length:
            log.info("generating '%s' report for '%s %s' (%d rows)", report_name,  name, surname, length)
            self.exporter.export(report_name, data)
        else:
            log.warning("No data to export")

    def generate_report_latest_month(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        name, surname = self.observer.get_name(observer_id)
        data, latest_month = self.reporter.get_latest_month_data_by(observer_id)
        report_name = f"{surname}-{latest_month.strftime("%Y%m")}"
        length = len(data)
        if length:
            log.info("generating '%s' report for '%s %s' (%d rows)", report_name,  name, surname, length)
            self.exporter.export(report_name, data)
        else:
            log.warning("No data to export")

class GenerateSummaryUseCase:
    def __init__(
        self,
        consent: ConsentService,
        observer: ObserverRepo,
        summarizer: SummaryService,
        display: DisplayService,
    ) -> None:
        self.consent = consent
        self.observer = observer
        self.summarizer = summarizer
        self.display = display

    def show_image_summary(self) -> None:
        self.consent.check_raises()
        observer_id = self.observer.get_default()
        data = self.summarizer.totals_by(observer_id)
        self.display.show_tabular(data)

    def show_sky_summary(self) -> None:
        self.consent.check_raises()
        data = self.summarizer.ranged_summary()
        self.display.show_tabular(data)
