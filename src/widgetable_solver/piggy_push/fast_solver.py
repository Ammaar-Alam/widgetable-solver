from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class FastSearchConfig:
    beam_width: int = 256
    lookahead_hits: int = 4


def solve_fast(
    board: Board,
    *,
    move_limit: int | None = None,
    beam_width: int = 256,
    lookahead_hits: int = 4,
) -> tuple[str, ...] | None:
    return FastSolver(
        move_limit=move_limit,
        config=FastSearchConfig(beam_width=beam_width, lookahead_hits=lookahead_hits),
    ).solve(board)


def beam_breakout(
    board: Board,
    *,
    beam_width: int = 256,
    max_hit_depth: int = 4,
) -> tuple[str, ...] | None:
    return FastSolver(
        config=FastSearchConfig(beam_width=beam_width, lookahead_hits=max_hit_depth),
    ).beam_breakout(board)


class FastSolver:
    def __init__(
        self,
        *,
        move_limit: int | None = None,
        config: FastSearchConfig | None = None,
    ) -> None:
        self.move_limit = move_limit
        self.config = config or FastSearchConfig()

    def solve(self, board: Board) -> tuple[str, ...] | None:
        if self.move_limit is not None and self.move_limit < len(board.pigs):
            return None

        current = board
        plan: list[str] = []

        while not current.is_cleared():
            if self._cannot_finish_within_limit(current, len(plan)):
                return None

            pig = self._best_greedy_action(current)
            if pig is not None:
                plan.append(pig.id)
                current = current.move(pig.id)
                continue

            breakout = self.beam_breakout(current)
            if breakout is None:
                return None

            for pig_id in breakout:
                plan.append(pig_id)
                current = current.move(pig_id)
                if self._cannot_finish_within_limit(current, len(plan)):
                    return None

        return tuple(plan)

    def beam_breakout(self, board: Board) -> tuple[str, ...] | None:
        beam: list[tuple[Board, tuple[str, ...]]] = [(board, ())]
        seen: set[tuple[tuple[int, int, str], ...]] = {board.state_key()}

        for _ in range(self.config.lookahead_hits):
            next_beam: list[tuple[tuple[int, int, int, int, str], Board, tuple[str, ...]]] = []

            for state, path in beam:
                if exit_ids(state):
                    return path

                for pig in self._collision_candidates(state):
                    event = move_event(state, pig.id)
                    if event.kind is not MoveKind.HIT:
                        continue

                    next_state = event.board
                    next_key = next_state.state_key()
                    if next_key in seen:
                        continue

                    seen.add(next_key)
                    next_path = path + (pig.id,)
                    if exit_ids(next_state):
                        return next_path
                    next_beam.append((self._state_score(next_state), next_state, next_path))

            if not next_beam:
                return None

            next_beam.sort(reverse=True, key=lambda item: item[0])
            beam = [(state, path) for _, state, path in next_beam[: self.config.beam_width]]

        for state, path in beam:
            if exit_ids(state):
                return path
        return None

    def _best_greedy_action(self, board: Board) -> Pig | None:
        for pig in self._ordered_candidates(board):
            event = move_event(board, pig.id)
            if event.kind is MoveKind.EXIT and pig.id in safe_exit_ids(board):
                return pig

        for pig in self._ordered_candidates(board):
            if move_event(board, pig.id).kind is MoveKind.EXIT:
                return pig

        best: tuple[tuple[int, int, int, int, str], Pig] | None = None
        for pig in self._collision_candidates(board):
            event = move_event(board, pig.id)
            if event.kind is not MoveKind.HIT:
                continue
            score = self._state_score(event.board)
            candidate = (score, pig)
            if best is None or candidate[0] > best[0]:
                best = candidate
        return best[1] if best is not None else None

    def _collision_candidates(self, board: Board) -> tuple[Pig, ...]:
        graph = immediate_blocker_graph(board)
        cycles = cycle_members(graph)
        cycle_candidates = tuple(pig for pig in self._ordered_candidates(board) if pig.id in cycles)
        if cycle_candidates:
            return cycle_candidates
        return self._ordered_candidates(board)

    def _ordered_candidates(self, board: Board) -> tuple[Pig, ...]:
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
        safe_exit_rank = 0 if pig.id in safe_exits else 1
        cycle_rank = 0 if event.kind is MoveKind.HIT and pig.id in cycles else 1
        unblocks = counts.get(pig.id, 0)
        stopper_value = stoppers.get(pig.id, 0)
        edge_distance = min(pig.x, pig.y, board.width - 1 - pig.x, board.height - 1 - pig.y)
        return (
            event.collision_cost,
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

    def _state_score(self, board: Board) -> tuple[int, int, int, int, str]:
        residual = static_zero_peel_residual(board)
        graph = immediate_blocker_graph(board)
        removed_by_peel = len(board.pigs) - len(residual.pigs)
        cycle_count = len(cycle_members(graph))
        stopper_total = sum(stopper_values(board).values())
        return (
            removed_by_peel,
            len(exit_ids(board)),
            -cycle_count,
            -stopper_total,
            repr(board.state_key()),
        )

    def _cannot_finish_within_limit(self, board: Board, taps_used: int) -> bool:
        return self.move_limit is not None and taps_used + len(board.pigs) > self.move_limit
