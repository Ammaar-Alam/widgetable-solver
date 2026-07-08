from widgetable_solver.cli import build_parser
from widgetable_solver.piggy_push.runner import DEFAULT_GRID_HEIGHT, DEFAULT_GRID_WIDTH


def test_run_command_defaults_to_dry_run():
    parser = build_parser()

    args = parser.parse_args(["piggy-push", "run"])

    assert args.command == "piggy-push"
    assert args.piggy_command == "run"
    assert args.live is False


def test_run_command_requires_explicit_live_flag():
    parser = build_parser()

    args = parser.parse_args(["piggy-push", "run", "--live"])

    assert args.live is True


def test_piggy_push_commands_accept_solver_strategy():
    parser = build_parser()

    solve_args = parser.parse_args(["piggy-push", "solve-state", "state.json", "--strategy", "fast"])
    run_args = parser.parse_args(["piggy-push", "run", "--strategy", "hybrid"])

    assert solve_args.strategy == "fast"
    assert run_args.strategy == "hybrid"


def test_overlay_commands_accept_debug_detections_flag():
    parser = build_parser()

    analyze_args = parser.parse_args(
        ["piggy-push", "analyze", "image.png", "--debug-detections"]
    )
    run_args = parser.parse_args(["piggy-push", "run", "--debug-detections"])

    assert analyze_args.debug_detections is True
    assert run_args.debug_detections is True


def test_capture_and_run_accept_manual_actual_size_flag():
    parser = build_parser()

    capture_args = parser.parse_args(["capture", "--manual-actual-size"])
    run_args = parser.parse_args(["piggy-push", "run", "--manual-actual-size"])

    assert capture_args.manual_actual_size is True
    assert run_args.manual_actual_size is True


def test_piggy_push_image_commands_use_fine_grid_defaults():
    parser = build_parser()

    analyze_args = parser.parse_args(["piggy-push", "analyze", "image.png"])
    run_args = parser.parse_args(["piggy-push", "run"])

    assert analyze_args.grid_width == DEFAULT_GRID_WIDTH
    assert analyze_args.grid_height == DEFAULT_GRID_HEIGHT
    assert run_args.grid_width == DEFAULT_GRID_WIDTH
    assert run_args.grid_height == DEFAULT_GRID_HEIGHT
