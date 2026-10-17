# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import logging
from collections.abc import Sequence
from itertools import batched

# ---------------------
# Third party libraries
# ---------------------
from tabulate import tabulate

# ----------------
# Own dependencies
# ----------------
from ..ports import DisplayService, TabularData

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])


class StdoutDisplay(DisplayService):
    FORMATS = {
        "simple": "-",
        "grid": "=",
        "fancy_grid": "═",
        "outline": "=",
        "presto": "-",
        "plain": " ",
        "psql": "-",
    }

    def __init__(self, table_fmt: str = "simple", page_size: int | None = None) -> None:
        self.table_fmt = table_fmt
        self.page_size = page_size

    def show(self, text: str) -> None:
        print(text)

    def _title(self, output: str, title: str) -> tuple[str | None, str]:
        char = self.FORMATS.get(self.table_fmt)
        if char is None:
            return None, output
        lines = output.splitlines()
        first_line = lines[0]
        width = max(len(line) for line in lines)
        if self.table_fmt in ("grid", "fancy_grid", "outline", "psql"):
            first_line = lines[0]
            lines = lines[1:]
            title = f" {title} ".center(width - 2, char)
            title = f"{first_line[0]}{title}{first_line[-1]}"
        else:
            title = f" {title} ".center(width, char)
        return title, "\n".join(lines)

    def _print(
        self, table: TabularData, keys: Sequence[str] | None = None, title: str | None = None
    ) -> None:
        output = tabulate(table, headers=keys or "keys", tablefmt=self.table_fmt)
        if title is not None:
            new_title, output = self._title(output, title)
            title = new_title if new_title is not None else title
            print(title)
        print(output)

    def show_tabular(
        self, table: TabularData, keys: Sequence[str] | None = None, title: str | None = None
    ) -> None:
        if self.page_size is None:
            self._print(table, keys, title)
        else:
            for page in batched(table, self.page_size):
                self._print(page, keys, title)
                input("Press Enter to continue [Ctrl-C to abort] ...")


__all__ = ["StdoutDisplay"]
