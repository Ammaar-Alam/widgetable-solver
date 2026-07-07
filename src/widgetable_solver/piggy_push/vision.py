from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from statistics import median

import cv2
import numpy as np

from widgetable_solver.piggy_push.model import Board, Direction, Pig


@dataclass(frozen=True, slots=True)
class FieldCrop:
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def from_image_shape(cls, shape: tuple[int, ...]) -> FieldCrop:
        height, width = shape[:2]
        if height < width * 1.8:
            return cls(left=0, top=0, right=width, bottom=height)
        return cls(left=0, top=int(height * 0.30), right=width, bottom=int(height * 0.84))

    def apply(self, image: np.ndarray) -> np.ndarray:
        return image[self.top:self.bottom, self.left:self.right]


@dataclass(frozen=True, slots=True)
class Detection:
    id: str
    center: tuple[float, float]
    direction: Direction
    radius: float
    confidence: float


def quantize_detections(
    detections: tuple[Detection, ...],
    *,
    width: int,
    height: int,
    image_shape: tuple[int, ...],
    crop: FieldCrop | None = None,
    min_confidence: float = 0.5,
) -> Board:
    image_height, image_width = image_shape[:2]
    left = crop.left if crop else 0
    top = crop.top if crop else 0
    quant_width = (crop.right - crop.left) if crop else image_width
    quant_height = (crop.bottom - crop.top) if crop else image_height
    pigs: list[Pig] = []
    occupied: set[tuple[int, int]] = set()
    accepted_detections = _accepted_detections(detections, min_confidence=min_confidence)

    for detection in accepted_detections:
        x = min(width - 1, max(0, int((detection.center[0] - left) / quant_width * width)))
        y = min(height - 1, max(0, int((detection.center[1] - top) / quant_height * height)))
        if (x, y) in occupied:
            continue

        occupied.add((x, y))
        pigs.append(Pig(detection.id, x, y, detection.direction))

    return Board(
        width=width,
        height=height,
        pigs=tuple(pigs),
        collision_radius=_collision_radius(
            accepted_detections,
            width=width,
            height=height,
            image_shape=image_shape,
            crop=crop,
        ),
    )


def detect_pigs(image: np.ndarray, *, crop: FieldCrop | None = None) -> tuple[Detection, ...]:
    field = crop.apply(image) if crop else image
    hsv = cv2.cvtColor(field, cv2.COLOR_BGR2HSV)

    mask_a = cv2.inRange(
        hsv,
        np.array([0, 35, 120], dtype=np.uint8),
        np.array([18, 180, 255], dtype=np.uint8),
    )
    mask_b = cv2.inRange(
        hsv,
        np.array([165, 35, 120], dtype=np.uint8),
        np.array([179, 180, 255], dtype=np.uint8),
    )
    mask = cv2.bitwise_or(mask_a, mask_b)
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections: list[Detection] = []
    offset_x = crop.left if crop else 0
    offset_y = crop.top if crop else 0

    for index, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < 250:
            continue

        ellipse = _fit_ellipse(contour)
        if ellipse is None:
            continue

        (center_x, center_y), (axis_a, axis_b), angle = ellipse
        if axis_a < axis_b:
            axis_a, axis_b = axis_b, axis_a
            angle += 90.0
        angle = _oriented_angle_from_head(
            field,
            (float(center_x), float(center_y)),
            float(axis_a),
            angle,
        )

        detections.append(
            Detection(
                id=f"p{index}",
                center=(float(center_x + offset_x), float(center_y + offset_y)),
                direction=_direction_from_angle(angle),
                radius=float(max(axis_a, axis_b) / 2.0),
                confidence=min(1.0, max(0.0, area / 2200.0)),
            )
        )

    return tuple(sorted(detections, key=lambda detection: (detection.center[1], detection.center[0])))


def overlay_labels(
    detections: tuple[Detection, ...],
    solution: tuple[str, ...] | None = None,
) -> dict[str, str]:
    move_numbers = {pig_id: str(index + 1) for index, pig_id in enumerate(solution or ())}
    return {detection.id: move_numbers.get(detection.id, detection.id) for detection in detections}


def overlay_visible_detections(
    detections: tuple[Detection, ...],
    *,
    board: Board | None = None,
    debug_detections: bool = False,
) -> tuple[Detection, ...]:
    if debug_detections or board is None:
        return detections

    solved_ids = {pig.id for pig in board.pigs}
    return tuple(detection for detection in detections if detection.id in solved_ids)


def write_overlay(
    image: np.ndarray,
    detections: tuple[Detection, ...],
    output: Path,
    *,
    board: Board | None = None,
    solution: tuple[str, ...] | None = None,
    debug_detections: bool = False,
) -> None:
    overlay = image.copy()
    visible_detections = overlay_visible_detections(
        detections,
        board=board,
        debug_detections=debug_detections,
    )
    labels = overlay_labels(visible_detections, solution)
    planned_ids = set(solution or ())
    for detection in visible_detections:
        x, y = int(detection.center[0]), int(detection.center[1])
        cv2.circle(overlay, (x, y), int(detection.radius), (255, 0, 255), 2)
        dx, dy = detection.direction.vector
        cv2.arrowedLine(overlay, (x, y), (x + dx * 36, y + dy * 36), (0, 0, 255), 3)
        label = labels[detection.id]
        if detection.id in planned_ids:
            cv2.circle(overlay, (x, y), 20, (255, 255, 255), -1)
            cv2.circle(overlay, (x, y), 20, (0, 0, 255), 2)
            cv2.putText(
                overlay,
                label,
                (x - 9 if len(label) == 1 else x - 15, y + 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
            if debug_detections:
                cv2.putText(
                    overlay,
                    detection.id,
                    (x + 18, y - 18),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (50, 50, 50),
                    1,
                )
            continue
        cv2.putText(
            overlay,
            label,
            (x + 8, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (50, 50, 50),
            2,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), overlay)


def _fit_ellipse(contour: np.ndarray):
    if len(contour) < 5:
        return None
    return cv2.fitEllipse(contour)


def _accepted_detections(
    detections: tuple[Detection, ...],
    *,
    min_confidence: float,
) -> tuple[Detection, ...]:
    high_confidence = tuple(
        detection for detection in detections if detection.confidence >= min_confidence
    )
    if not high_confidence:
        return high_confidence

    typical_radius = median(detection.radius for detection in high_confidence)
    rescue_floor = max(0.35, min_confidence - 0.12)
    rescued = tuple(
        detection
        for detection in detections
        if rescue_floor <= detection.confidence < min_confidence
        and detection.radius >= typical_radius * 0.75
    )
    return tuple(
        sorted(
            high_confidence + rescued,
            key=lambda detection: (detection.center[1], detection.center[0], detection.id),
        )
    )


def _collision_radius(
    detections: tuple[Detection, ...],
    *,
    width: int,
    height: int,
    image_shape: tuple[int, ...],
    crop: FieldCrop | None = None,
) -> float:
    if not detections:
        return 0.0

    image_height, image_width = image_shape[:2]
    quant_width = (crop.right - crop.left) if crop else image_width
    quant_height = (crop.bottom - crop.top) if crop else image_height
    cell_size = min(quant_width / width, quant_height / height)
    if cell_size <= 0:
        return 0.0

    radius = median(detection.radius for detection in detections) / cell_size * 1.6
    return max(0.65, min(1.5, float(radius)))


def _direction_from_angle(angle: float) -> Direction:
    normalized = angle % 360.0
    if normalized < 22.5 or normalized >= 337.5:
        return Direction.RIGHT
    if normalized < 67.5:
        return Direction.DOWN_RIGHT
    if normalized < 112.5:
        return Direction.DOWN
    if normalized < 157.5:
        return Direction.DOWN_LEFT
    if normalized < 202.5:
        return Direction.LEFT
    if normalized < 247.5:
        return Direction.UP_LEFT
    if normalized < 292.5:
        return Direction.UP
    return Direction.UP_RIGHT


def _oriented_angle_from_head(
    image: np.ndarray,
    center: tuple[float, float],
    major_axis: float,
    angle: float,
) -> float:
    radians = math.radians(angle)
    unit_x = math.cos(radians)
    unit_y = math.sin(radians)
    sample_distance = max(8.0, major_axis * 0.28)
    sample_radius = max(6.0, major_axis * 0.13)
    center_x, center_y = center

    positive_score = _dark_detail_score(
        image,
        (center_x + unit_x * sample_distance, center_y + unit_y * sample_distance),
        sample_radius,
    )
    negative_score = _dark_detail_score(
        image,
        (center_x - unit_x * sample_distance, center_y - unit_y * sample_distance),
        sample_radius,
    )

    if negative_score > positive_score:
        return angle + 180.0
    return angle


def _dark_detail_score(
    image: np.ndarray,
    center: tuple[float, float],
    radius: float,
) -> float:
    image_height, image_width = image.shape[:2]
    center_x, center_y = center
    x0 = max(0, int(center_x - radius))
    x1 = min(image_width, int(center_x + radius) + 1)
    y0 = max(0, int(center_y - radius))
    y1 = min(image_height, int(center_y + radius) + 1)
    if x0 >= x1 or y0 >= y1:
        return 0.0

    patch = image[y0:y1, x0:x1]
    gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    yy, xx = np.ogrid[y0:y1, x0:x1]
    circle = (xx - center_x) ** 2 + (yy - center_y) ** 2 <= radius * radius
    dark = gray < 95
    return float(np.sum(dark & circle))
