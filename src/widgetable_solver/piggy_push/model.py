from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Direction(str, Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"

    @property
    def vector(self) -> tuple[int, int]:
        return {
            Direction.UP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
        }[self]


@dataclass(frozen=True, slots=True)
class Pig:
    id: str
    x: int
    y: int
    direction: Direction

    @property
    def cell(self) -> tuple[int, int]:
        return (self.x, self.y)

    def moved_to(self, x: int, y: int) -> Pig:
        return Pig(self.id, x, y, self.direction)


@dataclass(frozen=True, slots=True)
class Board:
    width: int
    height: int
    pigs: tuple[Pig, ...]

    def __post_init__(self) -> None:
        ids = [pig.id for pig in self.pigs]
        if len(ids) != len(set(ids)):
            raise ValueError("Pig ids must be unique")

        occupied = [pig.cell for pig in self.pigs]
        if len(occupied) != len(set(occupied)):
            raise ValueError("Pigs cannot occupy the same cell")

        for pig in self.pigs:
            if not self.contains(pig.x, pig.y):
                raise ValueError(f"Pig {pig.id} is outside the board")

    @classmethod
    def from_iterable(cls, width: int, height: int, pigs: Iterable[Pig]) -> Board:
        return cls(width=width, height=height, pigs=tuple(pigs))

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, pig_id: str) -> Pig:
        for pig in self.pigs:
            if pig.id == pig_id:
                return pig
        raise KeyError(pig_id)

    def occupied_cells(self, excluding: str | None = None) -> set[tuple[int, int]]:
        return {pig.cell for pig in self.pigs if pig.id != excluding}

    def move(self, pig_id: str) -> Board:
        pig = self.get(pig_id)
        dx, dy = pig.direction.vector
        occupied = self.occupied_cells(excluding=pig.id)
        x, y = pig.x, pig.y

        while True:
            next_x, next_y = x + dx, y + dy
            if not self.contains(next_x, next_y):
                return Board.from_iterable(
                    self.width,
                    self.height,
                    (candidate for candidate in self.pigs if candidate.id != pig.id),
                )
            if (next_x, next_y) in occupied:
                if (x, y) == pig.cell:
                    return self
                moved = pig.moved_to(x, y)
                return Board.from_iterable(
                    self.width,
                    self.height,
                    (
                        moved if candidate.id == pig.id else candidate
                        for candidate in self.pigs
                    ),
                )
            x, y = next_x, next_y

    def legal_moves(self) -> tuple[str, ...]:
        return tuple(pig.id for pig in self.pigs if self.move(pig.id) != self)

    def is_cleared(self) -> bool:
        return not self.pigs

    def state_key(self) -> tuple[tuple[int, int, str], ...]:
        return tuple(sorted((pig.x, pig.y, pig.direction.value) for pig in self.pigs))
