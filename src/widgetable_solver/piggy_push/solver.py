from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count

from widgetable_solver.piggy_push.model import Board, Pig


StateKey = tuple[tuple[int, int, str], ...]


@dataclass(frozen=True, slots=True)
class SearchStats:
    explored_states: int
    dead_states: int
    generated_states: int
    best_collision_cost: int | None


@dataclass(frozen=True, slots=True)
class Transition:
    board: Board
    collision_cost: int

    @property
    def exits(self) -> bool:
        return self.collision_cost == 0


def solve(
    board: Board,
    max_states: int = 250_000,
    move_limit: int | None = None,
) -> tuple[str, ...] | None:
    return Solver(max_states=max_states, move_limit=move_limit).solve(board)


class Solver:
    def __init__(self, max_states: int = 250_000, move_limit: int | None = None):
        self.max_states = max_states
        self.move_limit = move_limit
        self.explored_states = 0
        self.generated_states = 0
        self.best_collision_cost: int | None = None
        self._dead: set[StateKey] = set()

    @property
    def stats(self) -> SearchStats:
        return SearchStats(
            explored_states=self.explored_states,
            dead_states=len(self._dead),
            generated_states=self.generated_states,
            best_collision_cost=self.best_collision_cost,
        )

    def solve(self, board: Board) -> tuple[str, ...] | None:
        if self.move_limit is not None and self.move_limit < len(board.pigs):
            return None

        collision_budget = None
        if self.move_limit is not None:
            collision_budget = self.move_limit - len(board.pigs)

        sequence = count()
        queue: list[tuple[int, int, int, int, Board, tuple[str, ...]]] = []
        start_key = board.state_key()
        best_cost: dict[StateKey, int] = {start_key: 0}

        heappush(
            queue,
            (
                self._priority(board, 0),
                0,
                len(board.pigs),
                next(sequence),
                board,
                (),
            ),
        )

        while queue and self.explored_states < self.max_states:
            _, collision_cost, active_count, _, current, path = heappop(queue)
            key = current.state_key()
            if collision_cost != best_cost.get(key):
                continue
            if active_count != len(current.pigs):
                continue
            if current.is_cleared():
                self.best_collision_cost = collision_cost
                return path

            self.explored_states += 1
            any_transition = False

            for pig in self._ordered_candidates(current):
                transition = self._transition(current, pig)
                if transition is None:
                    continue
                any_transition = True

                next_collision_cost = collision_cost + transition.collision_cost
                if collision_budget is not None and next_collision_cost > collision_budget:
                    continue

                next_key = transition.board.state_key()
                if next_collision_cost >= best_cost.get(next_key, 10**12):
                    continue

                best_cost[next_key] = next_collision_cost
                self.generated_states += 1
                heappush(
                    queue,
                    (
                        self._priority(transition.board, next_collision_cost),
                        next_collision_cost,
                        len(transition.board.pigs),
                        next(sequence),
                        transition.board,
                        path + (pig.id,),
                    ),
                )

            if not any_transition:
                self._dead.add(key)

        return None

    def _transition(self, board: Board, pig: Pig) -> Transition | None:
        next_board = board.move(pig.id)
        if next_board == board:
            return None
        collision_cost = 0 if len(next_board.pigs) < len(board.pigs) else 1
        return Transition(board=next_board, collision_cost=collision_cost)

    def _priority(self, board: Board, collision_cost: int) -> int:
        return collision_cost + self._admissible_extra_lower_bound(board)

    def _admissible_extra_lower_bound(self, board: Board) -> int:
        if board.is_cleared() or self._static_zero_peel_clears(board):
            return 0
        return 1

    def _static_zero_peel_clears(self, board: Board) -> bool:
        current = board
        changed = True
        while changed and not current.is_cleared():
            changed = False
            for pig in self._ordered_candidates(current):
                transition = self._transition(current, pig)
                if transition is None or not transition.exits:
                    continue
                current = transition.board
                changed = True
                break
        return current.is_cleared()

    def _ordered_candidates(self, board: Board) -> tuple[Pig, ...]:
        return tuple(sorted(board.pigs, key=lambda pig: self._move_priority(board, pig)))

    def _move_priority(self, board: Board, pig: Pig) -> tuple[int, int, str]:
        transition = self._transition(board, pig)
        if transition is None:
            return (2, 10**9, pig.id)
        edge_distance = min(pig.x, pig.y, board.width - 1 - pig.x, board.height - 1 - pig.y)
        return (transition.collision_cost, edge_distance, pig.id)
