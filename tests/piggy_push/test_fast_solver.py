from widgetable_solver.piggy_push.fast_solver import beam_breakout, solve_fast
from widgetable_solver.piggy_push.model import Board, Direction, Pig


def test_fast_solver_removes_safe_exits_before_stopper_exits():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("safe", 4, 0, Direction.RIGHT),
            Pig("stopper", 3, 2, Direction.RIGHT),
            Pig("uses_stopper", 0, 2, Direction.RIGHT),
        ),
    )

    solution = solve_fast(board)

    assert solution is not None
    assert solution[0] == "safe"
    assert _clears(board, solution)


def test_fast_solver_breaks_blocker_cycle_with_collision_move():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.DOWN),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 1, 3, Direction.UP),
        ),
    )

    solution = solve_fast(board)

    assert solution is not None
    assert _collision_tap_count(board, solution) == 1
    assert _clears(board, solution)


def test_beam_breakout_returns_collision_plan_that_creates_an_exit():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.DOWN),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 1, 3, Direction.UP),
        ),
    )

    breakout = beam_breakout(board, beam_width=8, max_hit_depth=1)

    assert breakout is not None
    assert _collision_tap_count(board, breakout) == len(breakout)


def test_fast_solver_honors_move_limit():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.DOWN),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 1, 3, Direction.UP),
        ),
    )

    assert solve_fast(board, move_limit=4) is None
    assert solve_fast(board, move_limit=5) is not None


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
