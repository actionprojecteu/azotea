# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
from dataclasses import Field
from typing import Protocol, Any, ClassVar, TypeVar
from collections.abc import Sequence, Mapping


# Define una anotacion ataClass que representa a cualquer dataclass
class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
DataClass = TypeVar("DataClass", bound=DataclassLike)

TableRow = DataClass | Mapping[str, Any] | Sequence[Any]
TabularData = Sequence[TableRow]


class DisplayService(Protocol):
    def show(self, text: str) -> None: ...
    def show_tabular(self, table: Sequence[TabularData], keys: Sequence[str] | None = None) -> None: ...
