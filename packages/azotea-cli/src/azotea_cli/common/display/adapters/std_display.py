from collections.abc import Mapping, Sequence
from dataclasses import is_dataclass
from typing import Any

from tabulate import tabulate

from ..ports import DataClass, DisplayService

TableRow = DataClass | Mapping[str, Any] | Sequence[Any]
TabularData = Sequence[TableRow]


class StdoutDisplay(DisplayService):
    def __init__(self, tablefmt: str = "grid") -> None:
        self.tablefmt = tablefmt
    def show(self, text: str) -> None:
        print(text)

    def show_tabular(self, table: TabularData, keys: Sequence[str] | None = None) -> None:
        print(tabulate(table, headers=keys or "keys", tablefmt=self.tablefmt))


__all__ = ["StdoutDisplay"]
