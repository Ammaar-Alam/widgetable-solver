from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2

from widgetable_solver.piggy_push.model import Board, Direction, Pig
from widgetable_solver.piggy_push.solver import solve
from widgetable_solver.piggy_push.vision import (
    Detection,
    FieldCrop,
    detect_pigs,
    quantize_detections,
    write_overlay,
)
from widgetable_solver.platform.iphone import capture_iphone, save_capture
from widgetable_solver.platform.mouse import Clicker


@dataclass(frozen=True, slots=True)
class ImageSolveResult:
    board: Board
    detections: tuple[Detection, ...]
    solution: tuple[str, ...] | None


def board_from_payload(payload: dict[str, Any]) -> Board:
    width = int(payload["width"])
    height = int(payload["height"])
    pigs = tuple(
        Pig(
            id=str(item["id"]),
            x=int(item["x"]),
            y=int(item["y"]),
            direction=Direction(str(item["direction"]).lower()),
        )
        for item in payload["pigs"]
    )
    return Board(width=width, height=height, pigs=pigs)


def solve_payload(payload: dict[str, Any]) -> list[str] | None:
    solution = solve(board_from_payload(payload))
    return list(solution) if solution is not None else None


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def analyze_image(
    image_path: Path,
    *,
    overlay: Path | None = None,
    grid_width: int = 10,
    grid_height: int = 14,
    min_confidence: float = 0.5,
) -> ImageSolveResult:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    crop = FieldCrop.from_image_shape(image.shape)
    detections = detect_pigs(image, crop=crop)
    board = quantize_detections(
        detections,
        width=grid_width,
        height=grid_height,
        image_shape=image.shape,
        min_confidence=min_confidence,
    )
    solution = solve(board)
    if overlay is not None:
        write_overlay(image, detections, overlay)
    return ImageSolveResult(board=board, detections=detections, solution=solution)


def solve_image(image_path: Path, *, grid_width: int = 10, grid_height: int = 14) -> list[str] | None:
    result = analyze_image(image_path, grid_width=grid_width, grid_height=grid_height)
    return list(result.solution) if result.solution is not None else None


def capture_once(output: Path, *, position: bool = True):
    return save_capture(output, position=position)


def run_once(
    *,
    live: bool = False,
    overlay: Path | None = None,
    settle_seconds: float = 0.45,
    grid_width: int = 10,
    grid_height: int = 14,
) -> ImageSolveResult:
    window, image = capture_iphone(position=True)
    crop = FieldCrop.from_image_shape(image.shape)
    detections = detect_pigs(image, crop=crop)
    board = quantize_detections(detections, width=grid_width, height=grid_height, image_shape=image.shape)
    solution = solve(board)

    if overlay is not None:
        write_overlay(image, detections, overlay)

    if not live or solution is None:
        return ImageSolveResult(board=board, detections=detections, solution=solution)

    detection_by_id = {detection.id: detection for detection in detections}
    clicker = Clicker.for_window(window)
    for pig_id in solution:
        detection = detection_by_id.get(pig_id)
        if detection is None:
            raise RuntimeError(f"Missing detection for planned click: {pig_id}")
        clicker.click_window_point(detection.center[0], detection.center[1])
        time.sleep(settle_seconds)

    return ImageSolveResult(board=board, detections=detections, solution=solution)
