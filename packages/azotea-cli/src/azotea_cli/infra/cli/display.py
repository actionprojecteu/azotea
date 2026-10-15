from collections.abc import Sequence

from tabulate import tabulate

from azotea_cli.common.ports import DisplayService
from azotea_cli.common.models import DataClass

class StdoutDisplay(DisplayService):
    def show(self, text: str) -> None:
        print(text)

    def show_tabular(self, table: Sequence[DataClass]) -> None:
        print(tabulate(table, headers="keys", tablefmt="grid"))


__all__ = ["StdoutDisplay"]
