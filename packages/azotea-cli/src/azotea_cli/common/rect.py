# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import re
from typing import NamedTuple

# ----------------
# Own dependencies
# ----------------
from azotea_cli.common.errors import AzoteaError


class InvalidRectStringError(AzoteaError):
    """Rectangle string incorrectly formatted"""


class Point(NamedTuple):
    x: int
    y: int

    def __mul__(self, rhs: int) -> "Point":
        return Point(self.x * rhs, self.y * rhs)

    def __floordiv__(self, rhs: int) -> "Point":
        return Point(self.x // rhs, self.y // rhs)

    @classmethod
    def zero(cls) -> "Point":
        return cls(0, 0)


PATTERN: re.Pattern[str] = re.compile(r"\[(\d+):(\d+),(\d+):(\d+)\]")


class Rect(NamedTuple):
    x1: int
    y1: int
    x2: int
    y2: int

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Rect":
        return cls(p1.x, p1.y, p2.x, p2.y)

    @classmethod
    def from_string(cls, value: str) -> "Rect":
        match = re.fullmatch(PATTERN, value.strip())
        if match is None:
            raise InvalidRectStringError(f"{value!r}")
        x1, y1, x2, y2 = map(int, match.groups())
        return cls(x1, y1, x2, y2)

    def width(self) -> int:
        return self.x2 - self.x1

    def height(self) -> int:
        return self.y2 - self.y1

    def dimensions(self) -> tuple[int, int]:
        return self.x2 - self.x1, self.y2 - self.y1

    def origin(self) -> Point:
        return Point(self.x1, self.y1)

    def central(self) -> Point:
        return Point((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def contains(self, other: "Rect") -> bool:
        return (
            (self.x1 <= other.x1)
            and (self.y1 <= other.y1)
            and (other.x2 <= self.x2)
            and (other.y2 <= self.y2)
        )

    def recenter_on(self, screen: "Rect") -> "Rect":
        c_screen = screen.central()
        c_self = self.central()
        dx = c_screen.x - c_self.x
        dy = c_screen.y - c_self.y
        return self + Point(dx, dy)

    def __str__(self) -> str:
        """as a numpy slice"""
        return f"[{self.y1}:{self.y2},{self.x1}:{self.x2}]"

    def __add__(self, rhs: Point) -> "Rect":
        return Rect(self.x1 + rhs.x, self.y1 + rhs.y, self.x2 + rhs.x, self.y2 + rhs.y)

    def __mul__(self, rhs: int) -> "Rect":
        return Rect(self.x1 * rhs, self.y1 * rhs, self.x2 * rhs, self.y2 * rhs)

    def __floordiv__(self, rhs: int) -> "Rect":
        return Rect(self.x1 // rhs, self.y1 // rhs, self.x2 // rhs, self.y2 // rhs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rect):
            return NotImplemented
        return (
            self.x1 == other.x1
            and self.y1 == other.y1
            and self.x2 == other.x2
            and self.y2 == other.y2
        )
