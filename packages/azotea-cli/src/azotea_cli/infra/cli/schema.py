# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# standard library
# ----------------
import logging
import uuid
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta
from itertools import batched

# ---------------------
# Third party libraries
# ---------------------
#from lica.cli import execute
from lica_cli import execute
from lica_cli.validate import vdate
from lica_log import LogLevel

# ---------------
# Own dependecies
# ---------------
from azotea_cli import __version__
from azotea_cli.infra.sqlalchemy.database.adapters.decouple import DcplDatabase
from azotea_cli.infra.sqlalchemy import  Config, Date, Model, Time, sqa_logging

# ----------------
# Module constants
# ----------------

DESCRIPTION = "AZOTEA Database initial schema generation tool"

START_DATE = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
END_DATE = datetime(year=2050, month=12, day=31, hour=23, minute=59, second=59, microsecond=99999)


# -----------------------
# Module global variables
# -----------------------

# get the module logger
log = logging.getLogger(__name__.split(".")[-1])
# create the database object
db = DcplDatabase("DATABASE_URL")

# -------------------
# Auxiliary functions
# -------------------

def since() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-s",
        "--since",
        type=vdate,
        default=START_DATE,
        metavar="<YYYY-MM-DD>",
        help="Start date for Date dimension (default %(default)s)",
    )
    return parser

def until() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-u",
        "--until",
        type=vdate,
        default=END_DATE,
        metavar="<YYYY-MM-DD>",
        help="End date for Date dimension (default %(default)s)",
    )
    return parser


def seconds() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-e",
        "--seconds",
        type=int,
        choices=[i for i in range(1, 61)],
        default=1,
        help="Default seconds resolution (default %(default)s)",
    )
    return parser


def batch() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=10000,
        help="Date/Time database transaction batch size (default %(default)s)",
    )
    return parser


def julian_day(date: datetime) -> float:
    """Returns the Julian day number of a date at 0h UTC."""
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    return (date.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045) - 0.5


class TimeIterator:
    def __init__(self, step_seconds=1):
        self.step = timedelta(seconds=step_seconds)
        self.current = datetime(
            year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        self.limit = datetime(year=2000, month=1, day=2, hour=0, minute=0, second=0, microsecond=0)

    def __iter__(self):
        return self

    def __next__(self) -> datetime:
        x = self.current
        if x == self.limit:
            raise StopIteration
        self.current += self.step
        return x


class DateIterator:
    def __init__(self, from_date: datetime, to_date: datetime):
        self.step = timedelta(days=1)
        self.current = from_date
        self.limit = to_date

    def __iter__(self):
        return self

    def __next__(self) -> datetime:
        x = self.current
        if x > self.limit:
            raise StopIteration
        self.current += self.step
        return x


# -------------
# CLI Functions
# -------------


def cli_populate_date(args: Namespace) -> None:
    log.info("Generating Date values")
    date_iterator = DateIterator(from_date=args.since, to_date=args.until)
    date_objs = (
        Date(
            date_id=d.year * 10000 + d.month * 100 + d.day,
            sql_date=d.strftime("%Y-%m-%d"),
            day=int(d.strftime("%d")),
            date=d.strftime("%d/%m/%Y"),
            day_year=int(d.strftime("%j")),
            julian_day=julian_day(d),
            weekday=d.strftime("%A"),
            weekday_abbr=d.strftime("%a"),
            weekday_num=int(d.strftime("%w")),  # 0 = Sunday
            month=d.strftime("%B"),
            month_num=int(d.strftime("%m")),
            month_abbr=d.strftime("%b"),
            year=int(d.strftime("%Y")),
        )
        for d in date_iterator
    )
    for i, batch in enumerate(batched(date_objs, args.batch_size), start=1):
        log.info("Writing Date batch #%d (%d records)", i, len(batch))
        with db.session() as session:
            with session.begin():
                for obj in batch:
                    session.add(obj)


def cli_populate_time(args: Namespace) -> None:
    log.info("Generating Time values")
    time_iterator = TimeIterator(step_seconds=args.seconds)
    time_objs = (
        Time(
            time_id=t.hour * 10000 + t.minute * 100 + t.second,
            time=t.strftime("%H:%M:%S"),
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            day_fraction=(t.hour * 3600 + t.minute * 60 + t.second) / (24 * 60 * 60),
        )
        for t in time_iterator
    )
    for i, batch in enumerate(batched(time_objs, args.batch_size), start=1):
        log.info("Writing Time batch #%d (%d records)", i, len(batch))
        with db.session() as session:
            with session.begin():
                for obj in batch:
                    session.add(obj)


def cli_populate_config(args: Namespace) -> None:
    id = Config(section="database", property="uuid", value=str(uuid.uuid4()))
    version = Config(section="database", property="version", value="03")
    with db.session() as session:
        with session.begin():
            session.add(id)
            session.add(version)


def cli_populate_all(args: Namespace) -> None:
    cli_populate_date(args)
    cli_populate_time(args)
    cli_populate_config(args)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "date", parents=[since(), until(), batch()], help="Load initial Date values"
    )
    p.set_defaults(func=cli_populate_date)
    p = subparser.add_parser(
        "time", parents=[seconds(), batch()], help="Load initial Time values"
    )
    p.set_defaults(func=cli_populate_time)
    p = subparser.add_parser(
        "all",
        parents=[since(), until(), seconds(), batch()],
        help="Load all initial values",
    )
    p.set_defaults(func=cli_populate_all)


def cli_main(args: Namespace) -> None:
    if args.log_level == LogLevel.DEBUG:
        sqa_logging(True)
    db.init()
    with db.engine.begin():
        Model.metadata.drop_all(bind=db.engine)
        Model.metadata.create_all(bind=db.engine)
        args.func(args)
    db.engine.dispose()


def main():
    """The main entry point specified by pyproject.toml"""
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description=DESCRIPTION,
        log_fmt="%(asctime)s [%(levelname)-8s] %(message)s"
    )


if __name__ == "__main__":
    main()
