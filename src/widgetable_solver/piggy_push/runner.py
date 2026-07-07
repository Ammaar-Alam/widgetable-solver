from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2

from widgetable_solver.piggy_push.model import Board, Direction, Pig
from widgetable_solver.piggy_push.solver import SolverStrategy, solve
from widgetable_solver.piggy_push.vision import (
    Detection,
    FieldCrop,
    detect_pigs,
    quantize_detections,
    write_overlay,
)
from widgetable_solver.platform.iphone import capture_iphone, save_capture
from widgetable_solver.platform.mouse import Clicker


DEFAULT_GRID_WIDTH = 40
DEFAULT_GRID_HEIGHT = 56


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
    move_limit = payload.get("move_limit")
    strategy = _strategy_from_value(payload.get("strategy", "hybrid"))
    solution = solve(
        board_from_payload(payload),
        move_limit=int(move_limit) if move_limit is not None else None,
        strategy=strategy,
    )
    return list(solution) if solution is not None else None


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def analyze_image(
    image_path: Path,
    *,
    overlay: Path | None = None,
    grid_width: int = DEFAULT_GRID_WIDTH,
    grid_height: int = DEFAULT_GRID_HEIGHT,
    min_confidence: float = 0.5,
    strategy: SolverStrategy = "hybrid",
    debug_detections: bool = False,
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
        crop=crop,
        min_confidence=min_confidence,
    )
    solution = solve(board, strategy=strategy)
    if overlay is not None:
        write_overlay(
            image,
            detections,
            overlay,
            board=board,
            solution=solution,
            debug_detections=debug_detections,
        )
    return ImageSolveResult(board=board, detections=detections, solution=solution)


def solve_image(
    image_path: Path,
    *,
    grid_width: int = DEFAULT_GRID_WIDTH,
    grid_height: int = DEFAULT_GRID_HEIGHT,
    strategy: SolverStrategy = "hybrid",
    debug_detections: bool = False,
) -> list[str] | None:
    result = analyze_image(
        image_path,
        grid_width=grid_width,
        grid_height=grid_height,
        strategy=strategy,
        debug_detections=debug_detections,
    )
    return list(result.solution) if result.solution is not None else None


def capture_once(output: Path, *, position: bool = True):
    return save_capture(output, position=position)


def run_once(
    *,
    live: bool = False,
    overlay: Path | None = None,
    settle_seconds: float = 0.45,
    grid_width: int = DEFAULT_GRID_WIDTH,
    grid_height: int = DEFAULT_GRID_HEIGHT,
    strategy: SolverStrategy = "hybrid",
    debug_detections: bool = False,
) -> ImageSolveResult:
    window, image = capture_iphone(position=True)
    crop = FieldCrop.from_image_shape(image.shape)
    detections = detect_pigs(image, crop=crop)
    board = quantize_detections(
        detections,
        width=grid_width,
        height=grid_height,
        image_shape=image.shape,
        crop=crop,
    )
    solution = solve(board, strategy=strategy)

    if overlay is not None:
        write_overlay(
            image,
            detections,
            overlay,
            board=board,
            solution=solution,
            debug_detections=debug_detections,
        )

    if not live or solution is None:
        return ImageSolveResult(board=board, detections=detections, solution=solution)

    clicker = Clicker.for_window(window)
    while solution:
        detection = next_click_detection(detections, solution)
        clicker.click_window_point(detection.center[0], detection.center[1])
        time.sleep(settle_seconds)

        window, image = capture_iphone(position=False)
        crop = FieldCrop.from_image_shape(image.shape)
        detections = detect_pigs(image, crop=crop)
        board = quantize_detections(
            detections,
            width=grid_width,
            height=grid_height,
            image_shape=image.shape,
            crop=crop,
        )
        if board.is_cleared():
            solution = ()
            break
        solution = solve(board, strategy=strategy)
        if solution is None:
            break

    return ImageSolveResult(board=board, detections=detections, solution=solution)


def next_click_detection(
    detections: tuple[Detection, ...],
    solution: tuple[str, ...],
) -> Detection:
    pig_id = solution[0]
    detection_by_id = {detection.id: detection for detection in detections}
    detection = detection_by_id.get(pig_id)
    if detection is None:
        raise RuntimeError(f"Missing detection for planned click: {pig_id}")
    return detection


def _strategy_from_value(value: Any) -> SolverStrategy:
    strategy = str(value)
    if strategy in {"exact", "fast", "hybrid"}:
        return strategy
    raise ValueError(f"Unknown Piggy Push solver strategy: {strategy}")
