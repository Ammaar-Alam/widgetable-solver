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
