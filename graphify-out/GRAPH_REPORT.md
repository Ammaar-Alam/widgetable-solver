# Graph Report - widgetable-solver  (2026-07-07)

## Corpus Check
- 26 files · ~599,382 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 321 nodes · 618 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 206 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bb0be12c`
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
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `Board` - 53 edges
2. `Pig` - 40 edges
3. `Solver` - 17 edges
4. `Detection` - 16 edges
5. `FastSolver` - 15 edges
6. `move_event()` - 14 edges
7. `quantize_detections()` - 14 edges
8. `Widgetable Solver Piggy Push Design` - 12 edges
9. `analyze_image()` - 10 edges
10. `MoveKind` - 10 edges

## Surprising Connections (you probably didn't know these)
- `test_parse_image_data_url_accepts_png_payload()` --calls--> `parse_image_data_url()`  [INFERRED]
  tests/test_overlay_server.py → src/widgetable_solver/overlay_server.py
- `test_parse_image_data_url_rejects_non_images()` --calls--> `parse_image_data_url()`  [INFERRED]
  tests/test_overlay_server.py → src/widgetable_solver/overlay_server.py
- `test_run_command_defaults_to_dry_run()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py
- `test_run_command_requires_explicit_live_flag()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py
- `test_piggy_push_commands_accept_solver_strategy()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/widgetable_solver/cli.py

## Communities (18 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (25): code:toml ([build-system]), code:python (from __future__ import annotations), code:python (from widgetable_solver.piggy_push.model import Board, Direct), code:python (from __future__ import annotations), code:python (import numpy as np), code:python (from __future__ import annotations), code:bash (git init), code:bash (gh repo create widgetable-solver --private --source . --remo) (+17 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (21): Board, from_iterable(), Pig, test_clicking_blocked_pig_stops_before_blocker(), test_clicking_diagonal_pig_moves_along_diagonal_until_blocked(), test_clicking_unblocked_pig_removes_it_from_board(), test_radius_board_blocks_pigs_near_diagonal_ray(), test_state_key_is_independent_of_pig_order() (+13 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (30): Direction, analyze_image(), board_from_payload(), capture_once(), ImageSolveResult, load_state(), next_click_detection(), run_once() (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.24
Nodes (8): capture_iphone(), capture_window(), find_iphone_mirroring_window(), focus_iphone_mirroring(), move_iphone_mirroring_to_corner(), save_capture(), WindowBounds, Clicker

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (12): Architecture, CLI, Data Flow, Goal, Live Automation, Movement Rule, Repository Hygiene, Scope (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.22
Nodes (8): Enum, MoveKind, _collision_tap_count(), SearchStats, solve(), Solver, stats(), Transition

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (38): 10.1 Board bounds, 10.2 Pig center detection, 10.3 Heading estimation, 10.4 Collision shape approximation, 10.5 Transition validation from observed frames, 10.6 Solvable-state extraction, 10. Screenshot-to-state extraction, 11. Known results vs novel proposals (+30 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (22): all_blockers_graph(), blocker_counts(), can_never_be_stopper(), _cell_lies_on_forward_ray(), cycle_members(), exit_ids(), _forward_projection(), immediate_blocker_graph() (+14 more)

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
Cohesion: 0.13
Nodes (11): BaseHTTPRequestHandler, test_parse_image_data_url_accepts_png_payload(), test_parse_image_data_url_rejects_non_images(), ThreadingHTTPServer, analyze_image_bytes(), main(), OverlayRequestHandler, OverlayServerError (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.16
Nodes (20): test_direction_from_angle_preserves_diagonal_axes(), test_finer_grid_keeps_close_distinct_pigs(), test_low_confidence_detection_is_rejected(), test_low_confidence_full_size_detection_is_rescued(), test_overlay_labels_prefer_planned_move_numbers(), test_overlay_visible_detections_can_show_raw_debug_detections(), test_overlay_visible_detections_defaults_to_solved_board_pigs(), test_quantize_detections_can_use_field_crop_coordinates() (+12 more)

### Community 17 - "Community 17"
Cohesion: 0.29
Nodes (9): beam_breakout(), FastSearchConfig, solve_fast(), _clears(), _collision_tap_count(), test_beam_breakout_returns_collision_plan_that_creates_an_exit(), test_fast_solver_breaks_blocker_cycle_with_collision_move(), test_fast_solver_honors_move_limit() (+1 more)

## Knowledge Gaps
- **85 isolated node(s):** `width`, `height`, `pigs`, `code:bash (python3 -m venv .venv)`, `code:bash (widgetable capture --output captures/current.png)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Board` connect `Community 1` to `Community 2`, `Community 5`, `Community 7`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `Pig` connect `Community 1` to `Community 2`, `Community 5`, `Community 7`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `analyze_image()` connect `Community 2` to `Community 16`, `Community 15`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Board` (e.g. with `ImageSolveResult` and `MoveKind`) actually correct?**
  _`Board` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Pig` (e.g. with `ImageSolveResult` and `MoveKind`) actually correct?**
  _`Pig` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Solver` (e.g. with `MoveKind` and `Board`) actually correct?**
  _`Solver` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Detection` (e.g. with `ImageSolveResult` and `Board`) actually correct?**
  _`Detection` has 14 INFERRED edges - model-reasoned connections that need verification._