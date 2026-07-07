from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from widgetable_solver.piggy_push.runner import (
    analyze_image,
    capture_once,
    load_state,
    run_once,
    solve_image,
    solve_payload,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="widgetable")
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture")
    capture.add_argument("--output", type=Path, default=Path("captures/current.png"))
    capture.add_argument("--no-position", action="store_true")

    piggy = subparsers.add_parser("piggy-push")
    piggy_subparsers = piggy.add_subparsers(dest="piggy_command", required=True)

    analyze = piggy_subparsers.add_parser("analyze")
    analyze.add_argument("image", type=Path)
    analyze.add_argument("--overlay", type=Path)
    analyze.add_argument("--grid-width", type=int, default=10)
    analyze.add_argument("--grid-height", type=int, default=14)
    analyze.add_argument("--strategy", choices=("exact", "fast", "hybrid"), default="hybrid")

    solve_image_parser = piggy_subparsers.add_parser("solve-image")
    solve_image_parser.add_argument("image", type=Path)
    solve_image_parser.add_argument("--grid-width", type=int, default=10)
    solve_image_parser.add_argument("--grid-height", type=int, default=14)
    solve_image_parser.add_argument("--strategy", choices=("exact", "fast", "hybrid"), default="hybrid")

    solve_state = piggy_subparsers.add_parser("solve-state")
    solve_state.add_argument("state", type=Path)
    solve_state.add_argument("--strategy", choices=("exact", "fast", "hybrid"), default="hybrid")

    run = piggy_subparsers.add_parser("run")
    run.add_argument("--live", action="store_true")
    run.add_argument("--overlay", type=Path)
    run.add_argument("--settle-seconds", type=float, default=0.45)
    run.add_argument("--grid-width", type=int, default=10)
    run.add_argument("--grid-height", type=int, default=14)
    run.add_argument("--strategy", choices=("exact", "fast", "hybrid"), default="hybrid")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "capture":
        bounds = capture_once(args.output, position=not args.no_position)
        print(json.dumps({"output": str(args.output), "window": asdict(bounds)}, indent=2))
        return 0

    if args.command == "piggy-push":
        return _run_piggy(args)

    parser.error("Unknown command")
    return 2


def _run_piggy(args: argparse.Namespace) -> int:
    if args.piggy_command == "analyze":
        result = analyze_image(
            args.image,
            overlay=args.overlay,
            grid_width=args.grid_width,
            grid_height=args.grid_height,
            strategy=args.strategy,
        )
        print(_result_json(result))
        return 0

    if args.piggy_command == "solve-image":
        solution = solve_image(
            args.image,
            grid_width=args.grid_width,
            grid_height=args.grid_height,
            strategy=args.strategy,
        )
        print(json.dumps({"solution": solution}, indent=2))
        return 0

    if args.piggy_command == "solve-state":
        payload = load_state(args.state)
        payload.setdefault("strategy", args.strategy)
        solution = solve_payload(payload)
        print(json.dumps({"solution": solution}, indent=2))
        return 0

    if args.piggy_command == "run":
        result = run_once(
            live=args.live,
            overlay=args.overlay,
            settle_seconds=args.settle_seconds,
            grid_width=args.grid_width,
            grid_height=args.grid_height,
            strategy=args.strategy,
        )
        print(_result_json(result))
        return 0

    raise ValueError(f"Unknown Piggy Push command: {args.piggy_command}")


def _result_json(result) -> str:
    return json.dumps(
        {
            "pigs": [
                {
                    "id": pig.id,
                    "x": pig.x,
                    "y": pig.y,
                    "direction": pig.direction.value,
                }
                for pig in result.board.pigs
            ],
            "detections": [
                {
                    "id": detection.id,
                    "center": [round(detection.center[0], 2), round(detection.center[1], 2)],
                    "direction": detection.direction.value,
                    "confidence": round(detection.confidence, 3),
                }
                for detection in result.detections
            ],
            "solution": list(result.solution) if result.solution is not None else None,
        },
        indent=2,
    )


if __name__ == "__main__":
    raise SystemExit(main())
