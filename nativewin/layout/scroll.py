"""Scrolling support and WM_MOUSEWHEEL forwarding rules."""

from __future__ import annotations

import ctypes
from typing import Optional, TYPE_CHECKING

from nativewin.core import win32

if TYPE_CHECKING:
    from nativewin.window.form import Window


# Controls that consume wheel events themselves
_MULTILINE_CLASS = "Edit"
_TRACKBAR_CLASS = "msctls_trackbar32"
_LISTBOX_CLASS = "ListBox"


def wheel_delta(wparam: int) -> int:
    """Extract signed wheel delta from WM_MOUSEWHEEL wParam."""
    return ctypes.c_short((wparam >> 16) & 0xFFFF).value


def should_forward_wheel(child_hwnd: win32.HWND) -> bool:
    """Return True if wheel event should bubble to parent scroll container."""
    if not win32.IS_WINDOWS or not child_hwnd:
        return False

    buf = ctypes.create_unicode_buffer(256)
    win32.user32.GetClassNameW(child_hwnd, buf, 256)
    class_name = buf.value

    if class_name == _LISTBOX_CLASS:
        style = win32.user32.GetWindowLongPtrW(child_hwnd, win32.GWL_STYLE)
        if style & win32.WS_VSCROLL:
            return False

    if class_name == _MULTILINE_CLASS:
        style = win32.user32.GetWindowLongPtrW(child_hwnd, win32.GWL_STYLE)
        if style & win32.ES_MULTILINE:
            return False

    if class_name == _TRACKBAR_CLASS:
        return False

    return True


def forward_wheel_to_parent(child_hwnd: win32.HWND, wparam: int, lparam: int) -> bool:
    """Forward WM_MOUSEWHEEL from child to parent unless consumed."""
    if not win32.IS_WINDOWS:
        return False

    if not should_forward_wheel(child_hwnd):
        return False

    parent = win32.user32.GetParent(child_hwnd)
    if not parent:
        return False

    pt = win32.POINT()
    pt.x = ctypes.c_int16(lparam & 0xFFFF).value
    pt.y = ctypes.c_int16((lparam >> 16) & 0xFFFF).value
    win32.user32.ScreenToClient(parent, ctypes.byref(pt))
    packed_lparam = (pt.y << 16) | (pt.x & 0xFFFF)
    win32.user32.SendMessageW(parent, win32.WM_MOUSEWHEEL, wparam, packed_lparam)
    return True


class ScrollState:
    """Vertical scroll offset for a scrollable window client area."""

    def __init__(self, window: "Window") -> None:
        self.window = window
        self.offset_y = 0
        self.content_height = 0
        self.viewport_height = 0

    def apply_wheel(self, delta: int) -> None:
        """Scroll content by wheel delta (positive = up)."""
        step = -delta // 4
        max_offset = max(0, self.content_height - self.viewport_height)
        self.offset_y = max(0, min(max_offset, self.offset_y + step))
        self.window.relayout()

    def clamp(self) -> None:
        max_offset = max(0, self.content_height - self.viewport_height)
        self.offset_y = max(0, min(max_offset, self.offset_y))
