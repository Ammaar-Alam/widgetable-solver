# Graph Report - widgetable-solver  (2026-07-06)

## Corpus Check
- 19 files · ~587,952 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 143 nodes · 220 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 64 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `99a4f776`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `Board` - 23 edges
2. `Pig` - 16 edges
3. `Widgetable Solver Piggy Push Design` - 12 edges
4. `ImageSolveResult` - 9 edges
5. `Solver` - 9 edges
6. `Widgetable Solver Piggy Push Implementation Plan` - 9 edges
7. `Task 1: Repository Foundation` - 9 edges
8. `_run_piggy()` - 8 edges
9. `analyze_image()` - 8 edges
10. `Detection` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_board_from_payload_builds_model()` --calls--> `board_from_payload()`  [INFERRED]
  tests/piggy_push/test_runner.py → src/widgetable_solver/piggy_push/runner.py
- `test_run_command_defaults_to_dry_run()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py
- `test_run_command_requires_explicit_live_flag()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py
- `test_clicking_unblocked_pig_removes_it_from_board()` --calls--> `Board`  [INFERRED]
  tests/piggy_push/test_model.py → src/widgetable_solver/piggy_push/model.py
- `test_clicking_unblocked_pig_removes_it_from_board()` --calls--> `Pig`  [INFERRED]
  tests/piggy_push/test_model.py → src/widgetable_solver/piggy_push/model.py

## Communities (14 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (16): code:python (from __future__ import annotations), code:python (from widgetable_solver.piggy_push.model import Board, Direct), code:python (from __future__ import annotations), code:python (import numpy as np), code:python (from __future__ import annotations), code:bash (git init), code:bash (gh repo create widgetable-solver --private --source . --remo), code:python (from widgetable_solver.piggy_push.model import Board, Direct) (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (9): Board, Pig, test_clicking_blocked_pig_stops_before_blocker(), test_clicking_diagonal_pig_moves_along_diagonal_until_blocked(), test_clicking_unblocked_pig_removes_it_from_board(), test_state_key_is_independent_of_pig_order(), test_solver_clears_single_pig(), test_solver_returns_clearing_sequence_for_interdependent_board() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.22
Nodes (14): analyze_image(), capture_once(), ImageSolveResult, load_state(), run_once(), solve_image(), write_overlay(), str (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.24
Nodes (8): capture_iphone(), capture_window(), find_iphone_mirroring_window(), focus_iphone_mirroring(), move_iphone_mirroring_to_corner(), save_capture(), WindowBounds, Clicker

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (12): Architecture, CLI, Data Flow, Goal, Live Automation, Movement Rule, Repository Hygiene, Scope (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (9): test_direction_from_angle_preserves_diagonal_axes(), test_low_confidence_detection_is_rejected(), test_quantize_detections_maps_centers_to_cells(), detect_pigs(), Detection, _direction_from_angle(), FieldCrop, _fit_ellipse() (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (7): Enum, Direction, from_iterable(), board_from_payload(), solve_payload(), test_board_from_payload_builds_model(), test_solve_payload_returns_solution_list()

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (4): SearchStats, solve(), Solver, stats()

### Community 8 - "Community 8"
Cohesion: 0.25
Nodes (7): code:bash (python3 -m venv .venv), code:bash (widgetable capture --output captures/current.png), code:json ({), Commands, Piggy Push Status, Setup, Widgetable Solver

### Community 9 - "Community 9"
Cohesion: 0.50
Nodes (3): height, pigs, width

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (9): code:toml ([build-system]), code:gitignore (.DS_Store), code:markdown (# Widgetable Solver), code:block4, code:block5, code:python ("""Widgetable solver package."""), code:python ("""Shared macOS automation helpers."""), code:python ("""Piggy Push solver package.""") (+1 more)

## Knowledge Gaps
- **36 isolated node(s):** `width`, `height`, `pigs`, `code:bash (python3 -m venv .venv)`, `code:bash (widgetable capture --output captures/current.png)` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Board` connect `Community 1` to `Community 2`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `Pig` connect `Community 1` to `Community 2`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `ImageSolveResult` connect `Community 2` to `Community 1`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Board` (e.g. with `ImageSolveResult` and `SearchStats`) actually correct?**
  _`Board` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Pig` (e.g. with `ImageSolveResult` and `SearchStats`) actually correct?**
  _`Pig` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ImageSolveResult` (e.g. with `Board` and `Direction`) actually correct?**
  _`ImageSolveResult` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Solver` (e.g. with `Board` and `Pig`) actually correct?**
  _`Solver` has 2 INFERRED edges - model-reasoned connections that need verification._