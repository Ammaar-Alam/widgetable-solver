from widgetable_solver.piggy_push.model import Direction
from widgetable_solver.piggy_push.vision import Detection, FieldCrop, _direction_from_angle, quantize_detections


def test_field_crop_constrains_to_image_bounds():
    crop = FieldCrop.from_image_shape((1000, 500, 3))

    assert crop.left == 0
    assert crop.right == 500
    assert 250 <= crop.top <= 340
    assert 780 <= crop.bottom <= 900


def test_quantize_detections_maps_centers_to_cells():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="p1", center=(220.0, 120.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
    )

    board = quantize_detections(detections, width=4, height=4, image_shape=(400, 400, 3))

    assert board.width == 4
    assert board.height == 4
    assert board.get("p0").cell == (1, 1)
    assert board.get("p1").cell == (2, 1)


def test_low_confidence_detection_is_rejected():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.2),
    )

    board = quantize_detections(detections, width=4, height=4, image_shape=(400, 400, 3), min_confidence=0.5)

    assert board.pigs == ()


def test_direction_from_angle_preserves_diagonal_axes():
    assert _direction_from_angle(44.0) is Direction.DOWN_RIGHT
    assert _direction_from_angle(134.0) is Direction.DOWN_LEFT
