# Widgetable Solver

macOS automation tools for solving Widgetable games from iPhone Mirroring.

The first supported game is Piggy Push.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

The live runner needs macOS Screen Recording and Accessibility permissions for the terminal or app that launches it.

## Commands

```bash
widgetable capture --output captures/current.png
widgetable piggy-push analyze data/examples/piggy_push/level-015-start.png --overlay overlays/analysis.png
widgetable piggy-push solve-state examples/simple_state.json
widgetable piggy-push solve-image data/examples/piggy_push/level-015-start.png
widgetable piggy-push run --dry-run
widgetable piggy-push run --live
```

Live mode is explicit. Dry-run mode captures, detects, solves, and writes overlays without clicking.

## Piggy Push Status

The board model and PAWS-Exact solver are deterministic and covered by tests. PAWS-Exact implements the collision-cost search from `docs/algorithm.md`: exit taps cost 0, collision/setup taps cost 1, and optional `move_limit` values become collision budgets. The first OpenCV detector can analyze the saved screenshots and write overlays, but live clicking should only be used after the overlay matches the visible board. Uncertain or duplicated detections should be treated as calibration data for the next detector pass.

State files use integer grid cells:

```json
{
  "width": 4,
  "height": 4,
  "move_limit": 3,
  "pigs": [
    {"id": "a", "x": 1, "y": 1, "direction": "right"},
    {"id": "b", "x": 3, "y": 1, "direction": "down"}
  ]
}
```
