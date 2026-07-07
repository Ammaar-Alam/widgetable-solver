from widgetable_solver.piggy_push.model import Direction
from widgetable_solver.piggy_push.runner import board_from_payload, solve_payload


def test_board_from_payload_builds_model():
    payload = {
        "width": 4,
        "height": 4,
        "pigs": [
            {"id": "a", "x": 1, "y": 2, "direction": "right"},
            {"id": "b", "x": 3, "y": 2, "direction": "down"},
        ],
    }

    board = board_from_payload(payload)

    assert board.width == 4
    assert board.height == 4
    assert board.get("a").direction is Direction.RIGHT
    assert board.get("b").cell == (3, 2)


def test_solve_payload_returns_solution_list():
    payload = {
        "width": 4,
        "height": 4,
        "pigs": [
            {"id": "a", "x": 1, "y": 1, "direction": "right"},
        ],
    }

    assert solve_payload(payload) == ["a"]


def test_solve_payload_honors_move_limit():
    payload = {
        "width": 4,
        "height": 4,
        "move_limit": 0,
        "pigs": [
            {"id": "a", "x": 1, "y": 1, "direction": "right"},
        ],
    }

    assert solve_payload(payload) is None
