from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count

from widgetable_solver.piggy_push.analysis import (
    MoveKind,
    blocker_counts,
    cycle_members,
    exit_ids,
    immediate_blocker_graph,
    move_event,
    safe_exit_ids,
    static_zero_peel_residual,
    stopper_values,
)
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
    blocker_id: str | None = None
    distance: int = 0

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
        start_board, start_macro = self._safe_peel_closure(board)
        start_key = start_board.state_key()
        best_cost: dict[StateKey, int] = {start_key: 0}

        heappush(
            queue,
            (
                self._priority(start_board, 0),
                0,
                len(start_board.pigs),
                next(sequence),
                start_board,
                start_macro,
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

            for pig in self.ordered_candidates(current):
                transition = self._transition(current, pig)
                if transition is None:
                    continue
                any_transition = True

                next_collision_cost = collision_cost + transition.collision_cost
                if collision_budget is not None and next_collision_cost > collision_budget:
                    continue

                next_board, safe_macro = self._safe_peel_closure(transition.board)
                next_key = next_board.state_key()
                if next_collision_cost >= best_cost.get(next_key, 10**12):
                    continue

                best_cost[next_key] = next_collision_cost
                self.generated_states += 1
                heappush(
                    queue,
                    (
                        self._priority(next_board, next_collision_cost),
                        next_collision_cost,
                        len(next_board.pigs),
                        next(sequence),
                        next_board,
                        path + (pig.id,) + safe_macro,
                    ),
                )

            if not any_transition:
                self._dead.add(key)

        return None

    def _transition(self, board: Board, pig: Pig) -> Transition | None:
        event = move_event(board, pig.id)
        if event.kind is MoveKind.ZERO:
            return None
        return Transition(
            board=event.board,
            collision_cost=event.collision_cost,
            blocker_id=event.blocker_id,
            distance=event.distance,
        )

    def _priority(self, board: Board, collision_cost: int) -> int:
        return collision_cost + self._admissible_extra_lower_bound(board)

    def _admissible_extra_lower_bound(self, board: Board) -> int:
        if static_zero_peel_residual(board).is_cleared():
            return 0
        return 1

    def _safe_peel_closure(self, board: Board) -> tuple[Board, tuple[str, ...]]:
        current = board
        plan: list[str] = []

        while not current.is_cleared():
            safe_ids = safe_exit_ids(current)
            if not safe_ids:
                break

            safe_pig = next(
                pig for pig in self.ordered_candidates(current) if pig.id in safe_ids
            )
            transition = self._transition(current, safe_pig)
            if transition is None or not transition.exits:
                break
            current = transition.board
            plan.append(safe_pig.id)

        return current, tuple(plan)

    def ordered_candidates(self, board: Board) -> tuple[Pig, ...]:
        graph = immediate_blocker_graph(board)
        counts = blocker_counts(graph)
        cycles = cycle_members(graph)
        safe_exits = safe_exit_ids(board)
        exits = exit_ids(board)
        stoppers = stopper_values(board)
        return tuple(
            sorted(
                board.pigs,
                key=lambda pig: self._move_priority(
                    board,
                    pig,
                    counts,
                    cycles,
                    safe_exits,
                    exits,
                    stoppers,
                ),
            )
        )

    def _move_priority(
        self,
        board: Board,
        pig: Pig,
        counts: dict[str, int],
        cycles: set[str],
        safe_exits: set[str],
        exits: set[str],
        stoppers: dict[str, int],
    ) -> tuple[int, int, int, int, int, int, int, int, int, int, str]:
        event = move_event(board, pig.id)
        if event.kind is MoveKind.ZERO:
            return (2, 1, 0, 0, 0, 1, 0, 0, 10**9, 0, pig.id)

        after = event.board
        residual = static_zero_peel_residual(after)
        removed_by_peel = len(board.pigs) - len(residual.pigs)
        exit_delta = len(exit_ids(after)) - len(exits)
        cycle_reduction = len(cycles) - len(cycle_members(immediate_blocker_graph(after)))
        collision_cost = event.collision_cost
        safe_exit_rank = 0 if pig.id in safe_exits else 1
        cycle_rank = 0 if event.kind is MoveKind.HIT and pig.id in cycles else 1
        unblocks = counts.get(pig.id, 0)
        stopper_value = stoppers.get(pig.id, 0)
        edge_distance = min(pig.x, pig.y, board.width - 1 - pig.x, board.height - 1 - pig.y)
        return (
            collision_cost,
            safe_exit_rank,
            -removed_by_peel,
            -exit_delta,
            -cycle_reduction,
            cycle_rank,
            -unblocks,
            stopper_value,
            edge_distance,
            -event.distance,
            pig.id,
        )
