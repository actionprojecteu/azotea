from collections.abc import Sequence

from tabulate import tabulate

from ..ports import DataClass, DisplayService

class StdoutDisplay(DisplayService):
    def show(self, text: str) -> None:
        print(text)

    def show_tabular(self, table: Sequence[DataClass], keys: Sequence[str] | None = None) -> None:
        print(tabulate(table, headers="keys", tablefmt="grid"))


__all__ = ["StdoutDisplay"]
