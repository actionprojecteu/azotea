from typing import Protocol
from collections.abc import Sequence


class ReportsService(Protocol):
   def foo(self) -> None: ...
