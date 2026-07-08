from __future__ import annotations

import argparse
import subprocess
import time

from widgetable_solver.platform.iphone import (
    _position_iphone_script,
    find_iphone_mirroring_window,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Move iPhone Mirroring and restore Actual Size without capturing."
    )
    parser.add_argument("--polls", type=int, default=8)
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()

    print(f"before: {find_iphone_mirroring_window()}")
    completed = subprocess.run(
        ["osascript", "-e", _position_iphone_script()],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stderr.strip() or completed.stdout.strip())
        return completed.returncode

    for index in range(args.polls):
        time.sleep(args.interval)
        print(f"after {index + 1}: {find_iphone_mirroring_window()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
