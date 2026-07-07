from widgetable_solver.piggy_push.model import Board, Direction, Pig
from widgetable_solver.piggy_push.solver import Solver, solve


def test_solver_clears_single_pig():
    board = Board(width=4, height=4, pigs=(Pig("a", 1, 1, Direction.RIGHT),))

    solution = solve(board)

    assert solution == ("a",)


def test_solver_returns_clearing_sequence_for_interdependent_board():
    board = Board(
        width=4,
        height=4,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.DOWN),
            Pig("c", 2, 2, Direction.UP),
        ),
    )

    solution = solve(board)

    assert solution is not None
    current = board
    for pig_id in solution:
        current = current.move(pig_id)
    assert current.is_cleared()


def test_solver_returns_none_when_no_pig_can_move():
    board = Board(
        width=3,
        height=1,
        pigs=(
            Pig("a", 0, 0, Direction.RIGHT),
            Pig("b", 1, 0, Direction.LEFT),
        ),
    )

    assert solve(board) is None


def test_solver_minimizes_collision_taps_before_total_order():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 0, 2, Direction.RIGHT),
            Pig("b", 2, 2, Direction.DOWN_RIGHT),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 3, 1, Direction.RIGHT),
            Pig("e", 1, 3, Direction.UP_RIGHT),
        ),
    )

    solution = solve(board)

    assert solution is not None
    assert _collision_tap_count(board, solution) == 1
    assert _clears(board, solution)


def test_solver_respects_move_limit_as_collision_budget():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 0, 2, Direction.RIGHT),
            Pig("b", 2, 2, Direction.DOWN_RIGHT),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 3, 1, Direction.RIGHT),
            Pig("e", 1, 3, Direction.UP_RIGHT),
        ),
    )

    assert solve(board, move_limit=5) is None
    assert solve(board, move_limit=6) is not None


def test_solver_prioritizes_safe_exits_before_useful_stoppers():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("safe", 4, 0, Direction.RIGHT),
            Pig("stopper", 3, 2, Direction.RIGHT),
            Pig("uses_stopper", 0, 2, Direction.RIGHT),
        ),
    )

    ordered_ids = tuple(pig.id for pig in Solver().ordered_candidates(board))

    assert ordered_ids.index("safe") < ordered_ids.index("stopper")


def test_solver_front_loads_provably_safe_exits():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("safe", 4, 0, Direction.RIGHT),
            Pig("stopper", 3, 2, Direction.RIGHT),
            Pig("uses_stopper", 0, 2, Direction.RIGHT),
        ),
    )

    solution = solve(board)

    assert solution is not None
    assert solution[0] == "safe"
    assert _clears(board, solution)


def test_solver_prioritizes_collision_moves_inside_blocker_cycles():
    board = Board(
        width=7,
        height=7,
        pigs=(
            Pig("a", 2, 2, Direction.RIGHT),
            Pig("b", 4, 2, Direction.DOWN),
            Pig("c", 4, 4, Direction.LEFT),
            Pig("d", 2, 4, Direction.UP),
            Pig("tail", 0, 2, Direction.RIGHT),
        ),
    )

    ordered_ids = tuple(pig.id for pig in Solver().ordered_candidates(board))

    assert ordered_ids.index("a") < ordered_ids.index("tail")


def _collision_tap_count(board: Board, solution: tuple[str, ...]) -> int:
    current = board
    collisions = 0
    for pig_id in solution:
        next_board = current.move(pig_id)
        if len(next_board.pigs) == len(current.pigs):
            collisions += 1
        current = next_board
    return collisions


def _clears(board: Board, solution: tuple[str, ...]) -> bool:
    current = board
    for pig_id in solution:
        current = current.move(pig_id)
    return current.is_cleared()
