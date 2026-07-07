# Graph Report - widgetable-solver  (2026-07-06)

## Corpus Check
- 20 files · ~594,078 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 217 nodes · 315 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 74 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `20b55ef4`
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
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]

## God Nodes (most connected - your core abstractions)
1. `Board` - 26 edges
2. `Pig` - 19 edges
3. `Solver` - 13 edges
4. `Widgetable Solver Piggy Push Design` - 12 edges
5. `ImageSolveResult` - 9 edges
6. `Detection` - 9 edges
7. `7. Heuristics and reductions` - 9 edges
8. `Widgetable Solver Piggy Push Implementation Plan` - 9 edges
9. `Task 1: Repository Foundation` - 9 edges
10. `_run_piggy()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_board_from_payload_builds_model()` --calls--> `board_from_payload()`  [INFERRED]
  tests/piggy_push/test_runner.py → src/widgetable_solver/piggy_push/runner.py
- `test_solve_payload_returns_solution_list()` --calls--> `solve_payload()`  [INFERRED]
  tests/piggy_push/test_runner.py → src/widgetable_solver/piggy_push/runner.py
- `test_solve_payload_honors_move_limit()` --calls--> `solve_payload()`  [INFERRED]
  tests/piggy_push/test_runner.py → src/widgetable_solver/piggy_push/runner.py
- `test_overlay_labels_prefer_planned_move_numbers()` --calls--> `overlay_labels()`  [INFERRED]
  tests/piggy_push/test_vision.py → src/widgetable_solver/piggy_push/vision.py
- `test_run_command_defaults_to_dry_run()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py

## Communities (16 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (25): code:toml ([build-system]), code:python (from __future__ import annotations), code:python (from widgetable_solver.piggy_push.model import Board, Direct), code:python (from __future__ import annotations), code:python (import numpy as np), code:python (from __future__ import annotations), code:bash (git init), code:bash (gh repo create widgetable-solver --private --source . --remo) (+17 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (16): Enum, Board, from_iterable(), Pig, Transition, test_clicking_blocked_pig_stops_before_blocker(), test_clicking_diagonal_pig_moves_along_diagonal_until_blocked(), test_clicking_unblocked_pig_removes_it_from_board() (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (21): Direction, analyze_image(), board_from_payload(), capture_once(), ImageSolveResult, load_state(), run_once(), solve_image() (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.24
Nodes (8): capture_iphone(), capture_window(), find_iphone_mirroring_window(), focus_iphone_mirroring(), move_iphone_mirroring_to_corner(), save_capture(), WindowBounds, Clicker

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (12): Architecture, CLI, Data Flow, Goal, Live Automation, Movement Rule, Repository Hygiene, Scope (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.22
Nodes (10): test_direction_from_angle_preserves_diagonal_axes(), test_low_confidence_detection_is_rejected(), test_overlay_labels_prefer_planned_move_numbers(), test_quantize_detections_maps_centers_to_cells(), detect_pigs(), Detection, _direction_from_angle(), FieldCrop (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (30): 10.1 Board bounds, 10.2 Pig center detection, 10.3 Heading estimation, 10.4 Collision shape approximation, 10.5 Transition validation from observed frames, 10.6 Solvable-state extraction, 10. Screenshot-to-state extraction, 11. Known results vs novel proposals (+22 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (4): SearchStats, solve(), Solver, stats()

### Community 8 - "Community 8"
Cohesion: 0.25
Nodes (7): code:bash (python3 -m venv .venv), code:bash (widgetable capture --output captures/current.png), code:json ({), Commands, Piggy Push Status, Setup, Widgetable Solver

### Community 9 - "Community 9"
Cohesion: 0.50
Nodes (3): height, pigs, width

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (12): 13. Failure cases and handling, code:text (paws/), code:python (@dataclass(frozen=True)), Collider mismatch, Continuous numerical instability, Final recommendation, Greedy dead ends, Heading ambiguity (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (10): 7.1 Exit-ray detection, 7.2 Blocker graph, 7.3 SCC analysis, 7.4 Deadlock detection, 7.5 Safe-peel reductions, 7.6 Move ordering, 7.7 Canonicalization of equivalent pigs, 7.8 Transposition table hashing (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (8): 3.1 Continuous geometric model, 3.2 Legal actions, 3.3 Collision raycast, 3.4 Transition function, 3.5 Goal test, 3.6 Cost function, 3.7 Discretized / quantized model, 3. Formal model

## Knowledge Gaps
- **85 isolated node(s):** `width`, `height`, `pigs`, `code:bash (python3 -m venv .venv)`, `code:bash (widgetable capture --output captures/current.png)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Board` connect `Community 1` to `Community 2`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Pig` connect `Community 1` to `Community 2`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Solver` connect `Community 7` to `Community 1`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Board` (e.g. with `ImageSolveResult` and `SearchStats`) actually correct?**
  _`Board` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Pig` (e.g. with `ImageSolveResult` and `SearchStats`) actually correct?**
  _`Pig` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Solver` (e.g. with `Board` and `Pig`) actually correct?**
  _`Solver` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ImageSolveResult` (e.g. with `Board` and `Direction`) actually correct?**
  _`ImageSolveResult` has 6 INFERRED edges - model-reasoned connections that need verification._