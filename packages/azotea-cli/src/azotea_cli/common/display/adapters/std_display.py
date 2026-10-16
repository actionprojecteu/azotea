from collections.abc import Sequence
from itertools import batched

from tabulate import tabulate

from ..ports import DisplayService, TabularData

class StdoutDisplay(DisplayService):
    def __init__(self, tablefmt: str = "grid", page_size: int | None = None) -> None:
        self.tablefmt = tablefmt
        self.page_size = page_size

    def show(self, text: str) -> None:
        print(text)

    def show_tabular(self, table: TabularData, keys: Sequence[str] | None = None) -> None:
        if self.page_size is None:
            print(tabulate(table, headers=keys or "keys", tablefmt=self.tablefmt))
        else:
            for page in batched(table, self.page_size):
                 print(tabulate(page, headers=keys or "keys", tablefmt=self.tablefmt))
                 input("Press Enter to continue [Ctrl-C to abort] ...")




__all__ = ["StdoutDisplay"]
