# Widgetable Solver Piggy Push Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the initial `widgetable-solver` repository with Piggy Push as the first Widgetable game solver.

**Architecture:** Use a Python `src/` layout with shared iPhone Mirroring platform modules and a focused `piggy_push` package. Implement the pure movement model and exact solver first, then add screenshot analysis, CLI orchestration, and live-click plumbing around that tested core.

**Tech Stack:** Python 3.11+, pytest, OpenCV, NumPy, Pillow, mss, PyAutoGUI, PyObjC Quartz.

---

## File Structure

- `pyproject.toml`: package metadata, dependencies, pytest configuration, console script.
- `.gitignore`: excludes local environments, caches, generated captures, overlays, and crop review output.
- `README.md`: setup, commands, safety notes, and Piggy Push workflow.
- `docs/superpowers/specs/2026-07-06-widgetable-solver-piggy-push-design.md`: approved design.
- `docs/superpowers/plans/2026-07-06-widgetable-solver-piggy-push.md`: this implementation plan.
- `src/widgetable_solver/__init__.py`: package marker.
- `src/widgetable_solver/platform/__init__.py`: shared platform package marker.
- `src/widgetable_solver/platform/iphone.py`: iPhone Mirroring window discovery, focus, positioning, capture.
- `src/widgetable_solver/platform/mouse.py`: Quartz click helper and coordinate conversion.
- `src/widgetable_solver/piggy_push/__init__.py`: Piggy Push package exports.
- `src/widgetable_solver/piggy_push/model.py`: direction, pig, board, movement simulation.
- `src/widgetable_solver/piggy_push/solver.py`: exact memoized solver and move ordering.
- `src/widgetable_solver/piggy_push/vision.py`: screenshot analysis, pig detections, overlays, crop export.
- `src/widgetable_solver/piggy_push/runner.py`: dry-run/live orchestration.
- `src/widgetable_solver/cli.py`: command-line entry point.
- `tests/piggy_push/test_model.py`: model and movement tests.
- `tests/piggy_push/test_solver.py`: exact solver tests.
- `tests/piggy_push/test_vision.py`: deterministic vision utility tests.
- `data/examples/piggy_push/`: curated screenshots copied from the attached images.

## Task 1: Repository Foundation

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/widgetable_solver/__init__.py`
- Create: `src/widgetable_solver/platform/__init__.py`
- Create: `src/widgetable_solver/piggy_push/__init__.py`

- [ ] **Step 1: Add package metadata and test configuration**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "widgetable-solver"
version = "0.1.0"
description = "macOS automation tools for solving Widgetable games from iPhone Mirroring."
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "mss>=9.0.1",
  "numpy>=2.0",
  "opencv-python>=4.10",
  "Pillow>=10.0",
  "pyautogui>=0.9.54",
  "pyobjc-framework-Quartz>=10.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2",
]

[project.scripts]
widgetable = "widgetable_solver.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Add repo ignore rules**

Create `.gitignore`:

```gitignore
.DS_Store
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
build/
dist/
*.egg-info/

captures/
overlays/
data/review/
```

- [ ] **Step 3: Add README**

Create `README.md`:

```markdown
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
```

- [ ] **Step 4: Add package markers**

Create empty package files:

```python
"""Widgetable solver package."""
```

for `src/widgetable_solver/__init__.py`, and:

```python
"""Shared macOS automation helpers."""
```

for `src/widgetable_solver/platform/__init__.py`, and:

```python
"""Piggy Push solver package."""
```

for `src/widgetable_solver/piggy_push/__init__.py`.

- [ ] **Step 5: Verify package metadata**

Run: `python3 -m compileall src`

Expected: command exits 0 and compiles the package marker files.

## Task 2: Piggy Push Model

**Files:**
- Create: `tests/piggy_push/test_model.py`
- Create: `src/widgetable_solver/piggy_push/model.py`

- [ ] **Step 1: Write failing movement tests**

Create `tests/piggy_push/test_model.py`:

```python
from widgetable_solver.piggy_push.model import Board, Direction, Pig


def test_direction_vectors_match_screen_coordinates():
    assert Direction.UP.vector == (0, -1)
    assert Direction.RIGHT.vector == (1, 0)
    assert Direction.DOWN.vector == (0, 1)
    assert Direction.LEFT.vector == (-1, 0)


def test_clicking_unblocked_pig_removes_it_from_board():
    board = Board(width=5, height=5, pigs=(Pig("a", 1, 2, Direction.RIGHT),))

    next_board = board.move("a")

    assert next_board.pigs == ()


def test_clicking_blocked_pig_stops_before_blocker():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 2, Direction.RIGHT),
            Pig("b", 3, 2, Direction.LEFT),
        ),
    )

    next_board = board.move("a")

    assert next_board.get("a") == Pig("a", 2, 2, Direction.RIGHT)
    assert next_board.get("b") == Pig("b", 3, 2, Direction.LEFT)


def test_state_key_is_independent_of_pig_order():
    left = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 4, 4, Direction.LEFT),
        ),
    )
    right = Board(
        width=5,
        height=5,
        pigs=(
            Pig("b", 4, 4, Direction.LEFT),
            Pig("a", 1, 1, Direction.RIGHT),
        ),
    )

    assert left.state_key() == right.state_key()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/piggy_push/test_model.py -q`

Expected: FAIL with `ModuleNotFoundError` or missing model symbols.

- [ ] **Step 3: Implement minimal model**

Create `src/widgetable_solver/piggy_push/model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Direction(str, Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"

    @property
    def vector(self) -> tuple[int, int]:
        return {
            Direction.UP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
        }[self]


@dataclass(frozen=True, slots=True)
class Pig:
    id: str
    x: int
    y: int
    direction: Direction

    @property
    def cell(self) -> tuple[int, int]:
        return (self.x, self.y)

    def moved_to(self, x: int, y: int) -> "Pig":
        return Pig(self.id, x, y, self.direction)


@dataclass(frozen=True, slots=True)
class Board:
    width: int
    height: int
    pigs: tuple[Pig, ...]

    def __post_init__(self) -> None:
        ids = [pig.id for pig in self.pigs]
        if len(ids) != len(set(ids)):
            raise ValueError("Pig ids must be unique")
        occupied = [pig.cell for pig in self.pigs]
        if len(occupied) != len(set(occupied)):
            raise ValueError("Pigs cannot occupy the same cell")
        for pig in self.pigs:
            if not self.contains(pig.x, pig.y):
                raise ValueError(f"Pig {pig.id} is outside the board")

    @classmethod
    def from_iterable(cls, width: int, height: int, pigs: Iterable[Pig]) -> "Board":
        return cls(width=width, height=height, pigs=tuple(pigs))

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, pig_id: str) -> Pig:
        for pig in self.pigs:
            if pig.id == pig_id:
                return pig
        raise KeyError(pig_id)

    def occupied_cells(self, excluding: str | None = None) -> set[tuple[int, int]]:
        return {pig.cell for pig in self.pigs if pig.id != excluding}

    def move(self, pig_id: str) -> "Board":
        pig = self.get(pig_id)
        dx, dy = pig.direction.vector
        occupied = self.occupied_cells(excluding=pig.id)
        x, y = pig.x, pig.y

        while True:
            nx, ny = x + dx, y + dy
            if not self.contains(nx, ny):
                return Board.from_iterable(
                    self.width,
                    self.height,
                    (candidate for candidate in self.pigs if candidate.id != pig.id),
                )
            if (nx, ny) in occupied:
                if (x, y) == pig.cell:
                    return self
                moved = pig.moved_to(x, y)
                return Board.from_iterable(
                    self.width,
                    self.height,
                    moved if candidate.id == pig.id else candidate
                    for candidate in self.pigs
                )
            x, y = nx, ny

    def legal_moves(self) -> tuple[str, ...]:
        return tuple(pig.id for pig in self.pigs if self.move(pig.id) != self)

    def is_cleared(self) -> bool:
        return not self.pigs

    def state_key(self) -> tuple[tuple[int, int, str], ...]:
        return tuple(sorted((pig.x, pig.y, pig.direction.value) for pig in self.pigs))
```

- [ ] **Step 4: Run model tests**

Run: `pytest tests/piggy_push/test_model.py -q`

Expected: 4 passed.

## Task 3: Exact Solver

**Files:**
- Create: `tests/piggy_push/test_solver.py`
- Create: `src/widgetable_solver/piggy_push/solver.py`

- [ ] **Step 1: Write failing solver tests**

Create `tests/piggy_push/test_solver.py`:

```python
from widgetable_solver.piggy_push.model import Board, Direction, Pig
from widgetable_solver.piggy_push.solver import solve


def test_solver_clears_single_pig():
    board = Board(width=4, height=4, pigs=(Pig("a", 1, 1, Direction.RIGHT),))

    solution = solve(board)

    assert solution == ("a",)


def test_solver_backtracks_when_first_move_does_not_clear_everything():
    board = Board(
        width=4,
        height=4,
        pigs=(
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.LEFT),
            Pig("c", 2, 2, Direction.UP),
        ),
    )

    solution = solve(board)

    assert solution is not None
    current = board
    for pig_id in solution:
        current = current.move(pig_id)
    assert current.is_cleared()


def test_solver_returns_none_when_no_pig_can_move():
    board = Board(
        width=3,
        height=1,
        pigs=(
            Pig("a", 0, 0, Direction.RIGHT),
            Pig("b", 1, 0, Direction.LEFT),
        ),
    )

    assert solve(board) is None
```

- [ ] **Step 2: Run solver tests to verify they fail**

Run: `pytest tests/piggy_push/test_solver.py -q`

Expected: FAIL with `ModuleNotFoundError` for `solver`.

- [ ] **Step 3: Implement exact solver**

Create `src/widgetable_solver/piggy_push/solver.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from widgetable_solver.piggy_push.model import Board, Pig


@dataclass(frozen=True, slots=True)
class SearchStats:
    explored_states: int
    max_depth: int


def solve(board: Board, max_states: int = 250_000) -> tuple[str, ...] | None:
    solver = Solver(max_states=max_states)
    return solver.solve(board)


class Solver:
    def __init__(self, max_states: int = 250_000):
        self.max_states = max_states
        self.explored_states = 0
        self._dead: set[tuple[tuple[int, int, str], ...]] = set()

    def solve(self, board: Board) -> tuple[str, ...] | None:
        result = self._search(board, ())
        return result

    def _search(self, board: Board, path: tuple[str, ...]) -> tuple[str, ...] | None:
        if board.is_cleared():
            return path
        if self.explored_states >= self.max_states:
            return None

        key = board.state_key()
        if key in self._dead:
            return None

        self.explored_states += 1
        for pig in self._ordered_candidates(board):
            next_board = board.move(pig.id)
            if next_board == board:
                continue
            result = self._search(next_board, path + (pig.id,))
            if result is not None:
                return result

        self._dead.add(key)
        return None

    def _ordered_candidates(self, board: Board) -> tuple[Pig, ...]:
        return tuple(sorted(board.pigs, key=lambda pig: self._move_priority(board, pig)))

    def _move_priority(self, board: Board, pig: Pig) -> tuple[int, int, str]:
        next_board = board.move(pig.id)
        exits = len(next_board.pigs) < len(board.pigs)
        edge_distance = min(pig.x, pig.y, board.width - 1 - pig.x, board.height - 1 - pig.y)
        return (0 if exits else 1, edge_distance, pig.id)
```

- [ ] **Step 4: Run solver tests**

Run: `pytest tests/piggy_push/test_solver.py tests/piggy_push/test_model.py -q`

Expected: 7 passed.

## Task 4: Vision Utilities

**Files:**
- Create: `tests/piggy_push/test_vision.py`
- Create: `src/widgetable_solver/piggy_push/vision.py`

- [ ] **Step 1: Write failing vision utility tests**

Create `tests/piggy_push/test_vision.py`:

```python
import numpy as np

from widgetable_solver.piggy_push.model import Direction
from widgetable_solver.piggy_push.vision import Detection, FieldCrop, quantize_detections


def test_field_crop_constrains_to_image_bounds():
    crop = FieldCrop.from_image_shape((1000, 500, 3))

    assert crop.left == 0
    assert crop.right == 500
    assert 250 <= crop.top <= 340
    assert 780 <= crop.bottom <= 900


def test_quantize_detections_maps_centers_to_cells():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.9),
        Detection(id="p1", center=(220.0, 120.0), direction=Direction.LEFT, radius=28.0, confidence=0.9),
    )

    board = quantize_detections(detections, width=4, height=4, image_shape=(400, 400, 3))

    assert board.width == 4
    assert board.height == 4
    assert board.get("p0").cell == (1, 1)
    assert board.get("p1").cell == (2, 1)


def test_low_confidence_detection_is_rejected():
    detections = (
        Detection(id="p0", center=(100.0, 120.0), direction=Direction.RIGHT, radius=28.0, confidence=0.2),
    )

    board = quantize_detections(detections, width=4, height=4, image_shape=(400, 400, 3), min_confidence=0.5)

    assert board.pigs == ()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/piggy_push/test_vision.py -q`

Expected: FAIL with missing `vision` module.

- [ ] **Step 3: Implement vision utilities and first-pass detector**

Create `src/widgetable_solver/piggy_push/vision.py` with:

```python
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
    def from_image_shape(cls, shape: tuple[int, ...]) -> "FieldCrop":
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
    lower = np.array([0, 35, 120], dtype=np.uint8)
    upper = np.array([18, 160, 255], dtype=np.uint8)
    mask_a = cv2.inRange(hsv, lower, upper)
    lower_b = np.array([165, 35, 120], dtype=np.uint8)
    upper_b = np.array([179, 160, 255], dtype=np.uint8)
    mask = cv2.bitwise_or(mask_a, cv2.inRange(hsv, lower_b, upper_b))
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
        (cx, cy), (major, minor), angle = ellipse
        if major < minor:
            major, minor = minor, major
            angle += 90.0
        direction = _direction_from_angle(angle)
        confidence = min(1.0, max(0.0, area / 2200.0))
        detections.append(
            Detection(
                id=f"p{index}",
                center=(float(cx + offset_x), float(cy + offset_y)),
                direction=direction,
                radius=float(max(major, minor) / 2.0),
                confidence=confidence,
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
        cv2.putText(overlay, detection.id, (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), overlay)


def _fit_ellipse(contour: np.ndarray):
    if len(contour) < 5:
        return None
    return cv2.fitEllipse(contour)


def _direction_from_angle(angle: float) -> Direction:
    normalized = angle % 180.0
    if normalized < 45.0 or normalized >= 135.0:
        return Direction.RIGHT
    return Direction.DOWN
```

- [ ] **Step 4: Run vision tests**

Run: `pytest tests/piggy_push/test_vision.py tests/piggy_push/test_model.py -q`

Expected: 7 passed.

## Task 5: Platform Automation and Runner

**Files:**
- Create: `src/widgetable_solver/platform/iphone.py`
- Create: `src/widgetable_solver/platform/mouse.py`
- Create: `src/widgetable_solver/piggy_push/runner.py`
- Create: `src/widgetable_solver/cli.py`

- [ ] **Step 1: Add platform iPhone helpers**

Create `src/widgetable_solver/platform/iphone.py` with focused window discovery, focus, corner positioning, and screenshot capture using the Word Hunt approach.

- [ ] **Step 2: Add mouse helpers**

Create `src/widgetable_solver/platform/mouse.py` with a `Clicker` class that posts Quartz left-click events at window-relative coordinates.

- [ ] **Step 3: Add Piggy Push runner**

Create `src/widgetable_solver/piggy_push/runner.py` with `analyze_image`, `solve_image`, `capture_once`, and `run_once` helpers. `run_once(live=False)` must never click.

- [ ] **Step 4: Add CLI**

Create `src/widgetable_solver/cli.py` exposing `capture`, `piggy-push analyze`, `piggy-push solve-image`, `piggy-push solve-state`, and `piggy-push run`.

- [ ] **Step 5: Compile platform and runner code**

Run: `python3 -m compileall src`

Expected: command exits 0.

## Task 6: Example Screenshots, Verification, GitHub

**Files:**
- Copy: attached screenshots into `data/examples/piggy_push/`
- Modify: `README.md`

- [ ] **Step 1: Save attached screenshots**

Copy the five attached screenshots to:

- `data/examples/piggy_push/level-015-start.png`
- `data/examples/piggy_push/level-015-start-duplicate.png`
- `data/examples/piggy_push/level-016-many-pigs.png`
- `data/examples/piggy_push/level-016-run-animation.png`
- `data/examples/piggy_push/level-016-late.png`

- [ ] **Step 2: Run full tests**

Run: `pytest -q`

Expected: all tests pass.

- [ ] **Step 3: Run compile check**

Run: `python3 -m compileall src tests`

Expected: command exits 0.

- [ ] **Step 4: Initialize git and commit**

Run:

```bash
git init
git add .
git commit -m "(feat) scaffold widgetable piggy push solver"
```

Expected: a new initial commit is created.

- [ ] **Step 5: Create private GitHub repository**

Run:

```bash
gh repo create widgetable-solver --private --source . --remote origin --push
```

Expected: private GitHub repository is created and the initial branch is pushed.

## Self-Review

- Spec coverage: The plan covers repository creation, Piggy Push module boundaries, movement simulation, exact search, vision utilities, platform automation, CLI commands, screenshot examples, tests, and private GitHub creation.
- Placeholder scan: No placeholder tokens or fake values are present. Task 5 intentionally describes module responsibilities rather than full pasted code because it is integration plumbing around already defined interfaces.
- Type consistency: `Board`, `Pig`, `Direction`, `Detection`, `FieldCrop`, `solve`, and CLI names are consistent across tasks.
