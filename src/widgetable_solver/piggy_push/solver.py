from __future__ import annotations

from dataclasses import dataclass

from widgetable_solver.piggy_push.model import Board, Pig


@dataclass(frozen=True, slots=True)
class SearchStats:
    explored_states: int
    dead_states: int


def solve(board: Board, max_states: int = 250_000) -> tuple[str, ...] | None:
    return Solver(max_states=max_states).solve(board)


class Solver:
    def __init__(self, max_states: int = 250_000):
        self.max_states = max_states
        self.explored_states = 0
        self._dead: set[tuple[tuple[int, int, str], ...]] = set()

    @property
    def stats(self) -> SearchStats:
        return SearchStats(
            explored_states=self.explored_states,
            dead_states=len(self._dead),
        )

    def solve(self, board: Board) -> tuple[str, ...] | None:
        return self._search(board, ())

    def _search(self, board: Board, path: tuple[str, ...]) -> tuple[str, ...] | None:
        if board.is_cleared():
            return path
        if self.explored_states >= self.max_states:
            return None

        key = board.state_key()
        if key in self._dead:
            return None

        self.explored_states += 1
        for pig in self._ordered_candidates(board):
            next_board = board.move(pig.id)
            if next_board == board:
                continue

            result = self._search(next_board, path + (pig.id,))
            if result is not None:
                return result

        self._dead.add(key)
        return None

    def _ordered_candidates(self, board: Board) -> tuple[Pig, ...]:
        return tuple(sorted(board.pigs, key=lambda pig: self._move_priority(board, pig)))

    def _move_priority(self, board: Board, pig: Pig) -> tuple[int, int, str]:
        next_board = board.move(pig.id)
        exits = len(next_board.pigs) < len(board.pigs)
        edge_distance = min(pig.x, pig.y, board.width - 1 - pig.x, board.height - 1 - pig.y)
        return (0 if exits else 1, edge_distance, pig.id)
