from collections.abc import Sequence
from typing import Protocol

from .models import DataClass


class DisplayService(Protocol):
    def show(self, message: str) -> None: ...
    def show_tabular(self, table: Sequence[DataClass]) -> None: ...
