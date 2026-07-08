from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import mss
import numpy as np
from PIL import Image


@dataclass(frozen=True, slots=True)
class WindowBounds:
    x: int
    y: int
    width: int
    height: int

    @property
    def monitor(self) -> dict[str, int]:
        return {
            "left": self.x,
            "top": self.y,
            "width": self.width,
            "height": self.height,
            "mon": 1,
        }


def find_iphone_mirroring_window() -> WindowBounds | None:
    import Quartz

    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID,
    )
    for window in windows:
        owner = str(window.get(Quartz.kCGWindowOwnerName, ""))
        name = str(window.get(Quartz.kCGWindowName, ""))
        if "iPhone Mirroring" not in owner and "iPhone" not in name:
            continue
        bounds = window.get(Quartz.kCGWindowBounds)
        if not bounds:
            continue
        return WindowBounds(
            x=int(bounds["X"]),
            y=int(bounds["Y"]),
            width=int(bounds["Width"]),
            height=int(bounds["Height"]),
        )
    return None


def focus_iphone_mirroring() -> None:
    script = """
    tell application "System Events"
        tell process "iPhone Mirroring"
            set frontmost to true
        end tell
    end tell
    """
    subprocess.run(["osascript", "-e", script], capture_output=True, check=False)
    time.sleep(0.15)


def move_iphone_mirroring_to_corner() -> WindowBounds | None:
    subprocess.run(["osascript", "-e", _position_iphone_script()], capture_output=True, check=False)
    time.sleep(0.7)
    return find_iphone_mirroring_window()


def _position_iphone_script() -> str:
    return """
    tell application "System Events"
        tell process "iPhone Mirroring"
            set frontmost to true
            delay 0.5
            click menu item "Bottom Right" of menu 1 of menu item "Move & Resize" of menu 1 of menu bar item "Window" of menu bar 1
        end tell
    end tell
    """


def capture_window(bounds: WindowBounds) -> np.ndarray:
    with mss.mss() as sct:
        screenshot = sct.grab(bounds.monitor)
    return np.array(screenshot)[:, :, :3]


def capture_iphone(
    *,
    position: bool = True,
    manual_actual_size: bool = False,
) -> tuple[WindowBounds, np.ndarray]:
    bounds = move_iphone_mirroring_to_corner() if position else find_iphone_mirroring_window()
    if bounds is None:
        raise RuntimeError("Could not find iPhone Mirroring window")
    if manual_actual_size:
        try:
            input("Press Command-0 in iPhone Mirroring, then press Enter here to capture...")
        except EOFError as error:
            raise RuntimeError("Manual Actual Size confirmation requires an interactive terminal") from error
        bounds = find_iphone_mirroring_window()
        if bounds is None:
            raise RuntimeError("Could not find iPhone Mirroring window")
    focus_iphone_mirroring()
    return bounds, capture_window(bounds)


def save_capture(
    output: Path,
    *,
    position: bool = True,
    manual_actual_size: bool = False,
) -> WindowBounds:
    bounds, image = capture_iphone(position=position, manual_actual_size=manual_actual_size)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(output)
    return bounds
