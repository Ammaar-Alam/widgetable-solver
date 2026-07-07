from widgetable_solver.piggy_push.model import Direction
from widgetable_solver.piggy_push.runner import board_from_payload, next_click_detection, solve_payload
from widgetable_solver.piggy_push.vision import Detection


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


def test_solve_payload_uses_requested_strategy():
    payload = {
        "width": 5,
        "height": 5,
        "strategy": "fast",
        "pigs": [
            {"id": "a", "x": 1, "y": 1, "direction": "right"},
            {"id": "b", "x": 3, "y": 1, "direction": "down"},
            {"id": "c", "x": 3, "y": 3, "direction": "left"},
            {"id": "d", "x": 1, "y": 3, "direction": "up"},
        ],
    }

    solution = solve_payload(payload)

    assert solution is not None
    assert len(solution) == 5


def test_next_click_detection_uses_current_frame_solution():
    detections = (
        Detection(id="p0", center=(10.0, 10.0), direction=Direction.RIGHT, radius=5.0, confidence=0.9),
        Detection(id="p1", center=(20.0, 10.0), direction=Direction.LEFT, radius=5.0, confidence=0.9),
    )

    detection = next_click_detection(detections, ("p1", "p0"))

    assert detection is detections[1]


def test_next_click_detection_rejects_stale_solution_ids():
    detections = (
        Detection(id="p0", center=(10.0, 10.0), direction=Direction.RIGHT, radius=5.0, confidence=0.9),
    )

    try:
        next_click_detection(detections, ("missing",))
    except RuntimeError as error:
        assert str(error) == "Missing detection for planned click: missing"
    else:
        raise AssertionError("Expected RuntimeError")
