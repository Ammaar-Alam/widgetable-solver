from widgetable_solver.piggy_push.analysis import (
    MoveKind,
    all_blockers_graph,
    blocker_counts,
    can_never_be_stopper,
    exit_ids,
    immediate_blocker_graph,
    move_event,
    safe_exit_ids,
    static_zero_peel_residual,
    stopper_values,
    strongly_connected_components,
)
from widgetable_solver.piggy_push.model import Board, Direction, Pig


def test_move_event_reports_exit_hit_and_zero_displacement():
    exit_board = Board(width=4, height=4, pigs=(Pig("a", 1, 1, Direction.RIGHT),))
    hit_board = Board(
        width=4,
        height=4,
        pigs=(
            Pig("a", 0, 1, Direction.RIGHT),
            Pig("b", 2, 1, Direction.LEFT),
        ),
    )
    zero_board = Board(
        width=4,
        height=4,
        pigs=(
            Pig("a", 0, 1, Direction.RIGHT),
            Pig("b", 1, 1, Direction.LEFT),
        ),
    )

    exit_event = move_event(exit_board, "a")
    hit_event = move_event(hit_board, "a")
    zero_event = move_event(zero_board, "a")

    assert exit_event.kind is MoveKind.EXIT
    assert exit_event.blocker_id is None
    assert exit_event.distance == 2
    assert hit_event.kind is MoveKind.HIT
    assert hit_event.blocker_id == "b"
    assert hit_event.distance == 1
    assert zero_event.kind is MoveKind.ZERO
    assert zero_event.blocker_id == "b"
    assert zero_event.distance == 0


def test_immediate_blocker_graph_and_counts():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("a", 0, 2, Direction.RIGHT),
            Pig("b", 3, 2, Direction.LEFT),
            Pig("c", 3, 4, Direction.UP),
        ),
    )

    graph = immediate_blocker_graph(board)

    assert graph == {"a": "b", "b": "a", "c": "b"}
    assert blocker_counts(graph) == {"a": 1, "b": 2}


def test_all_blockers_graph_reports_every_collinear_blocker_before_exit():
    board = Board(
        width=6,
        height=5,
        pigs=(
            Pig("a", 0, 2, Direction.RIGHT),
            Pig("b", 2, 2, Direction.LEFT),
            Pig("c", 4, 2, Direction.UP),
        ),
    )

    assert immediate_blocker_graph(board)["a"] == "b"
    assert all_blockers_graph(board)["a"] == ("b", "c")


def test_strongly_connected_components_find_blocker_cycles():
    graph = {
        "a": "b",
        "b": "c",
        "c": "a",
        "d": "c",
        "e": "f",
    }

    components = strongly_connected_components(graph)

    assert {"a", "b", "c"} in components
    assert {"d"} in components
    assert {"e"} in components
    assert {"f"} in components


def test_safe_exit_ids_excludes_potential_future_stoppers():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("safe", 4, 0, Direction.RIGHT),
            Pig("stopper", 3, 2, Direction.RIGHT),
            Pig("uses_stopper", 0, 2, Direction.RIGHT),
        ),
    )

    assert move_event(board, "safe").kind is MoveKind.EXIT
    assert move_event(board, "stopper").kind is MoveKind.EXIT
    assert can_never_be_stopper(board, board.get("safe")) is True
    assert can_never_be_stopper(board, board.get("stopper")) is False
    assert safe_exit_ids(board) == {"safe"}
    assert stopper_values(board) == {"safe": 0, "stopper": 1, "uses_stopper": 0}


def test_static_zero_peel_residual_keeps_collision_required_cycle():
    board = Board(
        width=5,
        height=5,
        pigs=(
            Pig("edge", 4, 0, Direction.RIGHT),
            Pig("a", 1, 1, Direction.RIGHT),
            Pig("b", 3, 1, Direction.DOWN),
            Pig("c", 3, 3, Direction.LEFT),
            Pig("d", 1, 3, Direction.UP),
        ),
    )

    residual = static_zero_peel_residual(board)

    assert exit_ids(board) == {"edge"}
    assert {pig.id for pig in residual.pigs} == {"a", "b", "c", "d"}
