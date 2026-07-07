from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
    min_confidence: float = 0.5,
) -> Board:
    image_height, image_width = image_shape[:2]
    pigs: list[Pig] = []
    occupied: set[tuple[int, int]] = set()

    for detection in detections:
        if detection.confidence < min_confidence:
            continue

        x = min(width - 1, max(0, int(detection.center[0] / image_width * width)))
        y = min(height - 1, max(0, int(detection.center[1] / image_height * height)))
        if (x, y) in occupied:
            continue

        occupied.add((x, y))
        pigs.append(Pig(detection.id, x, y, detection.direction))

    return Board(width=width, height=height, pigs=tuple(pigs))


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


def write_overlay(image: np.ndarray, detections: tuple[Detection, ...], output: Path) -> None:
    overlay = image.copy()
    for detection in detections:
        x, y = int(detection.center[0]), int(detection.center[1])
        cv2.circle(overlay, (x, y), int(detection.radius), (255, 0, 255), 2)
        dx, dy = detection.direction.vector
        cv2.arrowedLine(overlay, (x, y), (x + dx * 36, y + dy * 36), (0, 0, 255), 3)
        cv2.putText(
            overlay,
            detection.id,
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


def _direction_from_angle(angle: float) -> Direction:
    normalized = angle % 180.0
    if normalized < 22.5 or normalized >= 157.5:
        return Direction.RIGHT
    if normalized < 67.5:
        return Direction.DOWN_RIGHT
    if normalized < 112.5:
        return Direction.DOWN
    return Direction.DOWN_LEFT
