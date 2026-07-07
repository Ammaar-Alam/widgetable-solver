from widgetable_solver.piggy_push.model import Board, Direction, Pig
from widgetable_solver.piggy_push.solver import solve


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
