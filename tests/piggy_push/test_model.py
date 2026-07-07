from widgetable_solver.piggy_push.model import Board, Direction, Pig


def test_direction_vectors_match_screen_coordinates():
    assert Direction.UP.vector == (0, -1)
    assert Direction.UP_RIGHT.vector == (1, -1)
    assert Direction.RIGHT.vector == (1, 0)
    assert Direction.DOWN_RIGHT.vector == (1, 1)
    assert Direction.DOWN.vector == (0, 1)
    assert Direction.DOWN_LEFT.vector == (-1, 1)
    assert Direction.LEFT.vector == (-1, 0)
    assert Direction.UP_LEFT.vector == (-1, -1)


def test_clicking_unblocked_pig_removes_it_from_board():
    board = Board(width=5, height=5, pigs=(Pig("a", 1, 2, Direction.RIGHT),))

    next_board = board.move("a")

    assert next_board.pigs == ()


def test_clicking_blocked_pig_stops_before_blocker():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 2, Direction.RIGHT),
            Pig("b", 3, 2, Direction.LEFT),
        ),
    )

    next_board = board.move("a")

    assert next_board.get("a") == Pig("a", 2, 2, Direction.RIGHT)
    assert next_board.get("b") == Pig("b", 3, 2, Direction.LEFT)


def test_clicking_diagonal_pig_moves_along_diagonal_until_blocked():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.DOWN_RIGHT),
            Pig("b", 3, 3, Direction.LEFT),
        ),
    )

    next_board = board.move("a")

    assert next_board.get("a") == Pig("a", 2, 2, Direction.DOWN_RIGHT)
    assert next_board.get("b") == Pig("b", 3, 3, Direction.LEFT)


def test_radius_board_blocks_pigs_near_diagonal_ray():
    board = Board(
        width=20,
        height=20,
        collision_radius=1.1,
        pigs=(
            Pig("a", 15, 10, Direction.DOWN_LEFT),
            Pig("b", 13, 13, Direction.UP_LEFT),
        ),
    )

    next_board = board.move("a")

    assert next_board.get("a") == Pig("a", 14, 11, Direction.DOWN_LEFT)
    assert next_board.get("b") == Pig("b", 13, 13, Direction.UP_LEFT)


def test_state_key_is_independent_of_pig_order():
    left = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 4, 4, Direction.LEFT),
        ),
    )
    right = Board(
        width=5,
        height=5,
        pigs=(
            Pig("b", 4, 4, Direction.LEFT),
            Pig("a", 1, 1, Direction.RIGHT),
        ),
    )

    assert left.state_key() == right.state_key()
