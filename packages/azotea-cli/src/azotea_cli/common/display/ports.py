from dataclasses import Field
from typing import Protocol, Any, ClassVar, TypeVar
from collections.abc import Sequence

# Define una anotacion ataClass que representa a cualquer dataclass
class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
DataClass = TypeVar("DataClass", bound=DataclassLike)


class DisplayService(Protocol):
    def show(self, text: str) -> None: ...
    def show_tabular(self, table: Sequence[DataClass], keys: Sequence[str] | None = None) -> None: ...
