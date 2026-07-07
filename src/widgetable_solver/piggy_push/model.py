from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Iterable


class Direction(str, Enum):
    UP = "up"
    UP_RIGHT = "up_right"
    RIGHT = "right"
    DOWN_RIGHT = "down_right"
    DOWN = "down"
    DOWN_LEFT = "down_left"
    LEFT = "left"
    UP_LEFT = "up_left"

    @property
    def vector(self) -> tuple[int, int]:
        return {
            Direction.UP: (0, -1),
            Direction.UP_RIGHT: (1, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN_RIGHT: (1, 1),
            Direction.DOWN: (0, 1),
            Direction.DOWN_LEFT: (-1, 1),
            Direction.LEFT: (-1, 0),
            Direction.UP_LEFT: (-1, -1),
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
    collision_radius: float = 0.0

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
    def from_iterable(
        cls,
        width: int,
        height: int,
        pigs: Iterable[Pig],
        *,
        collision_radius: float = 0.0,
    ) -> Board:
        return cls(
            width=width,
            height=height,
            pigs=tuple(pigs),
            collision_radius=collision_radius,
        )

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
        if self.collision_radius > 0:
            return self._move_with_collision_radius(pig)

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
                    collision_radius=self.collision_radius,
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
                    collision_radius=self.collision_radius,
                )
            x, y = next_x, next_y

    def first_blocker(self, pig_id: str) -> tuple[Pig, int] | None:
        pig = self.get(pig_id)
        if self.collision_radius > 0:
            blocker = self._radius_blocker(pig)
            if blocker is None:
                return None
            blocking_pig, travel = blocker
            return (blocking_pig, self._travel_to_steps(pig, travel))

        dx, dy = pig.direction.vector
        pigs_by_cell = {candidate.cell: candidate for candidate in self.pigs if candidate.id != pig.id}
        x, y = pig.x, pig.y
        distance = 0

        while True:
            x += dx
            y += dy
            if not self.contains(x, y):
                return None
            blocker = pigs_by_cell.get((x, y))
            if blocker is not None:
                return (blocker, distance)
            distance += 1

    def exit_distance(self, pig_id: str) -> int:
        pig = self.get(pig_id)
        dx, dy = pig.direction.vector
        x, y = pig.x, pig.y
        distance = 0

        while True:
            next_x, next_y = x + dx, y + dy
            if not self.contains(next_x, next_y):
                return distance
            x, y = next_x, next_y
            distance += 1

    def legal_moves(self) -> tuple[str, ...]:
        return tuple(pig.id for pig in self.pigs if self.move(pig.id) != self)

    def is_cleared(self) -> bool:
        return not self.pigs

    def state_key(self) -> tuple[tuple[int, int, str], ...]:
        return tuple(sorted((pig.x, pig.y, pig.direction.value) for pig in self.pigs))

    def _move_with_collision_radius(self, pig: Pig) -> Board:
        blocker = self._radius_blocker(pig)
        if blocker is None:
            return Board.from_iterable(
                self.width,
                self.height,
                (candidate for candidate in self.pigs if candidate.id != pig.id),
                collision_radius=self.collision_radius,
            )

        _, travel = blocker
        steps = self._travel_to_steps(pig, travel)
        if steps <= 0:
            return self

        dx, dy = pig.direction.vector
        moved = pig.moved_to(pig.x + dx * steps, pig.y + dy * steps)
        if moved.cell in self.occupied_cells(excluding=pig.id):
            return self

        return Board.from_iterable(
            self.width,
            self.height,
            (moved if candidate.id == pig.id else candidate for candidate in self.pigs),
            collision_radius=self.collision_radius,
        )

    def _radius_blocker(self, pig: Pig) -> tuple[Pig, float] | None:
        dx, dy = pig.direction.vector
        step_length = math.hypot(dx, dy)
        unit_x = dx / step_length
        unit_y = dy / step_length
        exit_travel = self._exit_travel(pig, unit_x, unit_y)
        best: tuple[Pig, float] | None = None

        for candidate in self.pigs:
            if candidate.id == pig.id:
                continue

            relative_x = candidate.x - pig.x
            relative_y = candidate.y - pig.y
            projection = relative_x * unit_x + relative_y * unit_y
            if projection <= 0:
                continue

            perpendicular_sq = max(
                0.0,
                relative_x * relative_x + relative_y * relative_y - projection * projection,
            )
            if math.sqrt(perpendicular_sq) > self.collision_radius:
                continue

            contact_travel = max(0.0, projection - self.collision_radius)
            if contact_travel >= exit_travel:
                continue
            if best is None or contact_travel < best[1]:
                best = (candidate, contact_travel)

        return best

    def _exit_travel(self, pig: Pig, unit_x: float, unit_y: float) -> float:
        distances: list[float] = []
        if unit_x > 0:
            distances.append((self.width - pig.x) / unit_x)
        elif unit_x < 0:
            distances.append((pig.x + 1) / -unit_x)

        if unit_y > 0:
            distances.append((self.height - pig.y) / unit_y)
        elif unit_y < 0:
            distances.append((pig.y + 1) / -unit_y)

        return min(distances)

    def _travel_to_steps(self, pig: Pig, travel: float) -> int:
        dx, dy = pig.direction.vector
        return max(0, int(math.floor(travel / math.hypot(dx, dy))))
