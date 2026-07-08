import cv2
import numpy as np

from widgetable_solver.piggy_push.model import Direction
from widgetable_solver.piggy_push.vision import (
    Detection,
    FieldCrop,
    _direction_from_angle,
    detect_pigs,
    overlay_labels,
    overlay_visible_detections,
    quantize_detections,
)


def test_field_crop_constrains_to_image_bounds():
    crop = FieldCrop.from_image_shape((1000, 500, 3))

    assert crop.left == 0
    assert crop.right == 500
    assert 250 <= crop.top <= 340
    assert 780 <= crop.bottom <= 900


def test_field_crop_keeps_cropped_board_images_full_frame():
    crop = FieldCrop.from_image_shape((1408, 1584, 3))

    assert crop.left == 0
    assert crop.top == 0
    assert crop.right == 1584
    assert crop.bottom == 1408


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


def test_quantize_detections_can_use_field_crop_coordinates():
    detections = (
        Detection(id="p0", center=(150.0, 250.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="p1", center=(350.0, 450.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
    )
    crop = FieldCrop(left=100, top=200, right=500, bottom=600)

    board = quantize_detections(
        detections,
        width=4,
        height=4,
        image_shape=(800, 800, 3),
        crop=crop,
    )

    assert board.get("p0").cell == (0, 0)
    assert board.get("p1").cell == (2, 2)


def test_low_confidence_detection_is_rejected():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.2),
    )

    board = quantize_detections(detections, width=4, height=4, image_shape=(400, 400, 3), min_confidence=0.5)

    assert board.pigs == ()


def test_low_confidence_full_size_detection_is_rescued():
    detections = (
        Detection(id="strong", center=(300.0, 300.0), direction=Direction.RIGHT, radius=40.0, confidence=0.9),
        Detection(id="rescued", center=(700.0, 300.0), direction=Direction.LEFT, radius=38.0, confidence=0.42),
        Detection(id="fragment", center=(500.0, 300.0), direction=Direction.DOWN, radius=16.0, confidence=0.42),
    )

    board = quantize_detections(detections, width=20, height=20, image_shape=(1000, 1000, 3))

    assert {pig.id for pig in board.pigs} == {"strong", "rescued"}


def test_finer_grid_keeps_close_distinct_pigs():
    detections = (
        Detection(id="p0", center=(250.0, 300.0), direction=Direction.DOWN_LEFT, radius=28.0, confidence=0.9),
        Detection(id="p1", center=(330.0, 300.0), direction=Direction.DOWN_RIGHT, radius=28.0, confidence=0.9),
    )

    coarse_board = quantize_detections(detections, width=10, height=14, image_shape=(2000, 1200, 3))
    fine_board = quantize_detections(detections, width=20, height=28, image_shape=(2000, 1200, 3))

    assert len(coarse_board.pigs) == 1
    assert len(fine_board.pigs) == 2


def test_direction_from_angle_preserves_diagonal_axes():
    assert _direction_from_angle(44.0) is Direction.DOWN_RIGHT
    assert _direction_from_angle(134.0) is Direction.DOWN_LEFT
    assert _direction_from_angle(224.0) is Direction.UP_LEFT
    assert _direction_from_angle(316.0) is Direction.UP_RIGHT


def test_overlay_labels_prefer_planned_move_numbers():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="p7", center=(200.0, 120.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
        Detection(id="p9", center=(300.0, 120.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
    )

    labels = overlay_labels(detections, solution=("p7", "p0"))

    assert labels == {"p0": "2", "p7": "1", "p9": "p9"}


def test_overlay_visible_detections_defaults_to_solved_board_pigs():
    detections = (
        Detection(id="used", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="duplicate", center=(110.0, 120.0), direction=Direction.DOWN, radius=14.0, confidence=0.4),
        Detection(id="unused", center=(300.0, 120.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
    )
    board = quantize_detections(
        detections,
        width=4,
        height=4,
        image_shape=(400, 400, 3),
        min_confidence=0.5,
    )

    visible = overlay_visible_detections(detections, board=board)

    assert tuple(detection.id for detection in visible) == ("used", "unused")


def test_overlay_visible_detections_can_show_raw_debug_detections():
    detections = (
        Detection(id="used", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="duplicate", center=(110.0, 120.0), direction=Direction.DOWN, radius=14.0, confidence=0.4),
    )
    board = quantize_detections(
        detections,
        width=4,
        height=4,
        image_shape=(400, 400, 3),
        min_confidence=0.5,
    )

    visible = overlay_visible_detections(detections, board=board, debug_detections=True)

    assert visible == detections


def test_detect_pigs_handles_actual_size_mirroring_scale():
    image = np.full((412, 348, 3), (190, 238, 150), dtype=np.uint8)
    for center in ((130, 170), (165, 190), (200, 210)):
        cv2.ellipse(
            image,
            center,
            (18, 11),
            45,
            0,
            360,
            (214, 204, 255),
            -1,
        )

    detections = detect_pigs(image)

    assert len(detections) == 3
    assert all(detection.confidence >= 0.5 for detection in detections)
