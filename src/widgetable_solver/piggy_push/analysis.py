from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from widgetable_solver.piggy_push.model import Board, Pig


class MoveKind(str, Enum):
    EXIT = "exit"
    HIT = "hit"
    ZERO = "zero"


@dataclass(frozen=True, slots=True)
class MoveEvent:
    kind: MoveKind
    board: Board
    pig_id: str
    distance: int
    blocker_id: str | None = None

    @property
    def collision_cost(self) -> int:
        return 0 if self.kind is MoveKind.EXIT else 1

    @property
    def exits(self) -> bool:
        return self.kind is MoveKind.EXIT


def move_event(board: Board, pig_id: str) -> MoveEvent:
    if board.collision_radius > 0:
        blocker = board.first_blocker(pig_id)
        if blocker is None:
            return MoveEvent(
                kind=MoveKind.EXIT,
                board=board.move(pig_id),
                pig_id=pig_id,
                distance=board.exit_distance(pig_id),
            )

        blocking_pig, distance = blocker
        return MoveEvent(
            kind=MoveKind.ZERO if distance == 0 else MoveKind.HIT,
            board=board.move(pig_id),
            pig_id=pig_id,
            distance=distance,
            blocker_id=blocking_pig.id,
        )

    pig = board.get(pig_id)
    dx, dy = pig.direction.vector
    pigs_by_cell = {candidate.cell: candidate for candidate in board.pigs if candidate.id != pig.id}
    x, y = pig.x, pig.y
    distance = 0

    while True:
        next_x, next_y = x + dx, y + dy
        if not board.contains(next_x, next_y):
            return MoveEvent(
                kind=MoveKind.EXIT,
                board=board.move(pig_id),
                pig_id=pig_id,
                distance=distance,
            )

        blocker = pigs_by_cell.get((next_x, next_y))
        if blocker is not None:
            return MoveEvent(
                kind=MoveKind.ZERO if distance == 0 else MoveKind.HIT,
                board=board.move(pig_id),
                pig_id=pig_id,
                distance=distance,
                blocker_id=blocker.id,
            )

        x, y = next_x, next_y
        distance += 1


def immediate_blocker_graph(board: Board) -> dict[str, str]:
    graph: dict[str, str] = {}
    for pig in board.pigs:
        event = move_event(board, pig.id)
        if event.blocker_id is not None:
            graph[pig.id] = event.blocker_id
    return graph


def all_blockers_graph(board: Board) -> dict[str, tuple[str, ...]]:
    graph: dict[str, tuple[str, ...]] = {}

    for pig in board.pigs:
        blockers = [
            candidate
            for candidate in board.pigs
            if candidate.id != pig.id
            and _cell_lies_on_forward_ray(
                pig,
                candidate.cell,
                collision_radius=board.collision_radius,
            )
        ]
        blockers.sort(key=lambda candidate: _forward_projection(pig, candidate.cell))

        if blockers:
            graph[pig.id] = tuple(blocker.id for blocker in blockers)

    return graph


def blocker_counts(graph: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for blocker_id in graph.values():
        counts[blocker_id] = counts.get(blocker_id, 0) + 1
    return counts


def strongly_connected_components(graph: dict[str, str]) -> list[set[str]]:
    nodes = set(graph) | set(graph.values())
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[set[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        target = graph.get(node)
        if target is not None:
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] == indices[node]:
            component: set[str] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)

    return components


def cycle_members(graph: dict[str, str]) -> set[str]:
    members: set[str] = set()
    for component in strongly_connected_components(graph):
        if len(component) > 1:
            members.update(component)
        else:
            node = next(iter(component))
            if graph.get(node) == node:
                members.add(node)
    return members


def can_never_be_stopper(board: Board, candidate: Pig) -> bool:
    for pig in board.pigs:
        if pig.id == candidate.id:
            continue
        if _cell_lies_on_forward_ray(
            pig,
            candidate.cell,
            collision_radius=board.collision_radius,
        ):
            return False
    return True


def stopper_values(board: Board) -> dict[str, int]:
    return {
        candidate.id: sum(
            1
            for pig in board.pigs
            if pig.id != candidate.id
            and _cell_lies_on_forward_ray(
                pig,
                candidate.cell,
                collision_radius=board.collision_radius,
            )
        )
        for candidate in board.pigs
    }


def exit_ids(board: Board) -> set[str]:
    return {pig.id for pig in board.pigs if move_event(board, pig.id).exits}


def safe_exit_ids(board: Board) -> set[str]:
    safe: set[str] = set()
    for pig in board.pigs:
        event = move_event(board, pig.id)
        if event.exits and can_never_be_stopper(board, pig):
            safe.add(pig.id)
    return safe


def static_zero_peel_residual(board: Board) -> Board:
    current = board
    changed = True

    while changed and not current.is_cleared():
        changed = False
        for pig in current.pigs:
            event = move_event(current, pig.id)
            if not event.exits:
                continue
            current = event.board
            changed = True
            break

    return current


def _cell_lies_on_forward_ray(
    pig: Pig,
    cell: tuple[int, int],
    *,
    collision_radius: float = 0.0,
) -> bool:
    target_x, target_y = cell
    dx, dy = pig.direction.vector
    rel_x = target_x - pig.x
    rel_y = target_y - pig.y

    if rel_x == 0 and rel_y == 0:
        return False

    if collision_radius > 0:
        projection = _forward_projection(pig, cell)
        if projection <= 0:
            return False
        perpendicular_sq = max(
            0.0,
            rel_x * rel_x + rel_y * rel_y - projection * projection,
        )
        return perpendicular_sq**0.5 <= collision_radius

    steps: int | None = None
    if dx == 0:
        if rel_x != 0:
            return False
    else:
        if rel_x % dx != 0:
            return False
        steps = rel_x // dx

    if dy == 0:
        if rel_y != 0:
            return False
    else:
        if rel_y % dy != 0:
            return False
        y_steps = rel_y // dy
        if steps is None:
            steps = y_steps
        elif steps != y_steps:
            return False

    return steps is not None and steps > 0


def _forward_projection(pig: Pig, cell: tuple[int, int]) -> float:
    target_x, target_y = cell
    dx, dy = pig.direction.vector
    length = (dx * dx + dy * dy) ** 0.5
    return ((target_x - pig.x) * dx + (target_y - pig.y) * dy) / length
