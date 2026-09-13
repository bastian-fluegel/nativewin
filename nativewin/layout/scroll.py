"""Scrolling support: overflow scrollbars, wheel forwarding, 2D offsets."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

from nativewin.core import metrics, win32

if TYPE_CHECKING:
    from nativewin.window.form import Window


_MULTILINE_CLASS = "Edit"
_TRACKBAR_CLASS = "msctls_trackbar32"
_LISTBOX_CLASS = "ListBox"
_COMBO_CLASS = "ComboBox"


def wheel_delta(wparam: int) -> int:
    """Extract signed wheel delta from WM_MOUSEWHEEL / WM_MOUSEHWHEEL wParam."""
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

    if class_name in (_TRACKBAR_CLASS, _COMBO_CLASS):
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


def _scroll_info(min_value: int, max_value: int, page: int, pos: int) -> win32.SCROLLINFO:
    info = win32.SCROLLINFO()
    info.cbSize = ctypes.sizeof(win32.SCROLLINFO)
    info.fMask = win32.SIF_RANGE | win32.SIF_PAGE | win32.SIF_POS
    info.nMin = min_value
    info.nMax = max(min_value, max_value)
    info.nPage = max(1, page)
    info.nPos = pos
    return info


def track_pos(hwnd: win32.HWND, bar: int) -> int:
    """Read the thumb position (including live track) for a window scrollbar."""
    info = win32.SCROLLINFO()
    info.cbSize = ctypes.sizeof(win32.SCROLLINFO)
    info.fMask = win32.SIF_TRACKPOS | win32.SIF_POS
    if win32.user32.GetScrollInfo(hwnd, bar, ctypes.byref(info)):
        return int(info.nTrackPos)
    return int(info.nPos)


class ScrollState:
    """Horizontal and vertical scroll offsets for a window client area."""

    def __init__(self, window: "Window") -> None:
        self.window = window
        self.offset_x = 0
        self.offset_y = 0
        self.content_width = 0
        self.content_height = 0
        self.viewport_width = 0
        self.viewport_height = 0
        self.show_h = False
        self.show_v = False

    def max_x(self) -> int:
        return max(0, self.content_width - self.viewport_width)

    def max_y(self) -> int:
        return max(0, self.content_height - self.viewport_height)

    def apply_wheel(self, delta: int, horizontal: bool = False) -> None:
        """Scroll content by wheel delta (positive = up / left)."""
        step = -int(delta / 120) * metrics.scroll_line() * 3
        if step == 0:
            step = -1 if delta > 0 else 1
        if horizontal:
            self.offset_x = max(0, min(self.max_x(), self.offset_x + step))
        else:
            self.offset_y = max(0, min(self.max_y(), self.offset_y + step))
        self.window.relayout()

    def apply_command(self, bar: int, code: int, hwnd: win32.HWND) -> None:
        """Handle WM_HSCROLL / WM_VSCROLL codes."""
        line = metrics.scroll_line()
        if bar == win32.SB_HORZ:
            page = max(1, self.viewport_width)
            pos = self.offset_x
            limit = self.max_x()
        else:
            page = max(1, self.viewport_height)
            pos = self.offset_y
            limit = self.max_y()

        if code in (win32.SB_LINEUP, win32.SB_LINELEFT):
            pos -= line
        elif code in (win32.SB_LINEDOWN, win32.SB_LINERIGHT):
            pos += line
        elif code in (win32.SB_PAGEUP, win32.SB_PAGELEFT):
            pos -= page
        elif code in (win32.SB_PAGEDOWN, win32.SB_PAGERIGHT):
            pos += page
        elif code in (win32.SB_TOP, win32.SB_LEFT):
            pos = 0
        elif code in (win32.SB_BOTTOM, win32.SB_RIGHT):
            pos = limit
        elif code in (win32.SB_THUMBPOSITION, win32.SB_THUMBTRACK):
            pos = track_pos(hwnd, bar)
        elif code == win32.SB_ENDSCROLL:
            return
        pos = max(0, min(limit, pos))
        if bar == win32.SB_HORZ:
            self.offset_x = pos
        else:
            self.offset_y = pos
        self.window.relayout()

    def clamp(self) -> None:
        self.offset_x = max(0, min(self.max_x(), self.offset_x))
        self.offset_y = max(0, min(self.max_y(), self.offset_y))

    def sync_bars(self, hwnd: win32.HWND) -> None:
        """Show native scrollbars only when content overflows the viewport."""
        if not win32.IS_WINDOWS or not hwnd:
            return
        need_v = self.content_height > self.viewport_height
        need_h = self.content_width > self.viewport_width
        self.show_v = need_v
        self.show_h = need_h
        win32.user32.ShowScrollBar(hwnd, win32.SB_VERT, need_v)
        win32.user32.ShowScrollBar(hwnd, win32.SB_HORZ, need_h)
        if need_v:
            info = _scroll_info(
                0,
                max(0, self.content_height - 1),
                self.viewport_height,
                self.offset_y,
            )
            win32.user32.SetScrollInfo(hwnd, win32.SB_VERT, ctypes.byref(info), True)
        if need_h:
            info = _scroll_info(
                0,
                max(0, self.content_width - 1),
                self.viewport_width,
                self.offset_x,
            )
            win32.user32.SetScrollInfo(hwnd, win32.SB_HORZ, ctypes.byref(info), True)
