# Widgetable Solver Piggy Push Design

## Goal

Build a private macOS automation repository for Widgetable games, starting with Piggy Push. The first usable slice should detect a Piggy Push board from iPhone Mirroring screenshots, solve the board exactly, and optionally click the proven sequence on the mirrored phone.

## Scope

The repository is named `widgetable-solver`. Piggy Push lives under `src/widgetable_solver/piggy_push/` as the first game module. Shared iPhone Mirroring and mouse automation code lives under `src/widgetable_solver/platform/` so later Widgetable games can reuse it.

The initial implementation prioritizes a reliable foundation over broad game support:

- Save the attached Piggy Push screenshots as examples for offline development.
- Implement a deterministic puzzle model and exact solver.
- Implement screenshot capture, coordinate mapping, and click execution in isolated modules.
- Implement OpenCV-based pig detection with debug overlays and crop export.
- Add dry-run and overlay modes so solving can be checked before live clicks.
- Keep model training optional. If sprite recognition is not reliable enough, the crop export path will supply training data.

## Movement Rule

Each pig has a fixed facing direction. When clicked, that pig moves straight in its facing direction until it either hits another pig or exits the board. A pig that exits is removed. A pig that hits another pig stays on the board at the last free position before the blocker. The player loses when no sequence of remaining clicks can clear every pig.

## Architecture

The app is split into small modules with explicit boundaries:

- `platform.iphone`: find, focus, position, and capture the iPhone Mirroring window.
- `platform.mouse`: convert window-relative game coordinates to Quartz click events.
- `piggy_push.model`: immutable board, pig, direction, and movement simulation.
- `piggy_push.solver`: exact DFS/backtracking solver with memoized states and heuristic move ordering.
- `piggy_push.vision`: screenshot-to-board detection, crop export, and debug overlays.
- `piggy_push.runner`: one-level and continuous solving orchestration.
- `scripts/widgetable`: command-line entry point for dry runs, captures, overlays, and live solve.

The solver must be independently testable from hand-authored board states. Vision must be independently testable from image files. Live automation must be gated behind explicit `--live` flags.

## Data Flow

1. The runner focuses and positions iPhone Mirroring.
2. It captures a screenshot and passes it to Piggy Push vision.
3. Vision returns detected pigs with centers, directions, sizes, and confidence/debug artifacts.
4. The runner converts detections into a discrete board model.
5. The solver returns a click order that clears all pigs, or reports no solution with the best diagnostic state.
6. In dry-run mode, the runner writes an overlay and planned moves.
7. In live mode, the runner clicks each pig center, waits for movement to settle, then refreshes the screenshot before continuing or advancing to the next level.

## Solver Strategy

Use exact search, not a greedy-only strategy. Candidate moves are ordered so obvious edge-clearing pigs are tried first, matching the practical human strategy, but the solver backtracks if a greedy move blocks the puzzle.

The state key includes each remaining pig's quantized position and direction. This keeps repeated dead states from being re-explored. The solver returns the shortest found solution by default for the explored state graph, with a configurable cap for safety.

## Vision Strategy

Start with OpenCV:

- Crop the playable green field below the score/progress header and above the bottom buttons.
- Detect pig sprites by color segmentation around the pink body and dark outline.
- Estimate each pig's center, orientation, and footprint from contour geometry.
- Quantize positions onto an inferred grid so simulation can reason about blockers.
- Save debug overlays and uncertain crops under `data/review/`.

The implementation should make uncertainty visible. If direction or footprint confidence is low, dry-run should refuse live clicking and save artifacts for review.

## Live Automation

Reuse the Word Hunt style:

- `mss` captures the iPhone Mirroring window.
- AppleScript focuses and moves the iPhone Mirroring window to a stable corner.
- Quartz posts mouse click events.
- Window-relative coordinates are the canonical internal coordinate system.

Live clicking must wait between clicks long enough for the pig run animation to finish. The first version uses a conservative fixed delay plus optional screenshot-change settling. Later tuning can reduce latency.

## CLI

The first CLI exposes:

- `capture`: position the phone and save a screenshot.
- `analyze IMAGE`: detect pigs and write an overlay.
- `solve-state JSON`: solve a hand-authored state.
- `solve-image IMAGE`: detect and solve from a screenshot without clicking.
- `run --dry-run`: capture, detect, solve, and write overlays.
- `run --live`: perform the same path and click the solved sequence.

Live mode is explicit so test and debug commands cannot accidentally click the phone.

## Testing

Initial tests cover:

- Direction parsing and vector behavior.
- Pig movement until blocker or exit.
- State hashing independent of insertion order.
- Solver returns a full clearing sequence on simple and blocked puzzles.
- Solver reports no solution when the search space proves blocked.
- Vision utility functions for crop bounds, quantization, and confidence gating.

Live iPhone automation is validated with dry-run commands and overlays rather than unit tests.

## Repository Hygiene

The repo should use Python with a `src/` layout, `pytest`, type hints, and concise docs. The code should stay modular and avoid hardcoded secrets. Generated screenshots, crops, overlays, and local virtual environments are ignored by git except for curated example images intentionally stored under `data/examples/`.
