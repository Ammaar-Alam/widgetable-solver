from __future__ import annotations

import time
from dataclasses import dataclass

import pyautogui
from Quartz import (
    CGEventCreateMouseEvent,
    CGEventPost,
    CGEventSourceCreate,
    CGEventSetIntegerValueField,
    CGPointMake,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventSourceStateHIDSystemState,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
    kCGMouseEventPressure,
)

from widgetable_solver.platform.iphone import WindowBounds


@dataclass(frozen=True, slots=True)
class Clicker:
    window: WindowBounds
    screen_height: int

    @classmethod
    def for_window(cls, window: WindowBounds) -> Clicker:
        return cls(window=window, screen_height=pyautogui.size()[1])

    def click_window_point(self, x: float, y: float, *, hold: float = 0.03) -> None:
        screen_x = self.window.x + x
        quartz_y = self.screen_height - (self.window.y + y)
        source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
        point = CGPointMake(screen_x, quartz_y)

        down = CGEventCreateMouseEvent(source, kCGEventLeftMouseDown, point, kCGMouseButtonLeft)
        CGEventSetIntegerValueField(down, kCGMouseEventPressure, 255)
        CGEventPost(kCGHIDEventTap, down)
        time.sleep(hold)

        up = CGEventCreateMouseEvent(source, kCGEventLeftMouseUp, point, kCGMouseButtonLeft)
        CGEventSetIntegerValueField(up, kCGMouseEventPressure, 255)
        CGEventPost(kCGHIDEventTap, up)
