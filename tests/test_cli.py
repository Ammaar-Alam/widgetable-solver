from widgetable_solver.cli import build_parser


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
