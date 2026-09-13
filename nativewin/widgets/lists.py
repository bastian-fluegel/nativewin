"""List and selection widgets."""

from __future__ import annotations

from typing import List, Optional

from nativewin.core import win32
from nativewin.state.binding import State
from nativewin.widgets.base import Widget, _finalize


class ListBox(Widget):
    """Single-selection list box."""

    _class_name = "ListBox"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_BORDER
        | win32.WS_TABSTOP
        | win32.LBS_NOTIFY
        | win32.WS_VSCROLL
    )

    def __init__(
        self,
        items: Optional[List[str]] = None,
        bind: Optional[State] = None,
        height: int = 120,
    ) -> None:
        super().__init__()
        self._items = list(items or [])
        self._bind_state = bind
        self._fixed_height = height

    def preferred_height(self, width: int) -> int:
        return self._fixed_height

    def _on_created(self) -> None:
        for item in self._items:
            self.add_item(item)
        if self._bind_state is not None:
            self._bind_state.bind(self._on_state_changed)

    def _on_state_changed(self, value: str) -> None:
        self.select(value)

    def add_item(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(self.hwnd, 0x0180, 0, text)  # LB_ADDSTRING

    def clear(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(self.hwnd, 0x0184, 0, 0)  # LB_RESETCONTENT

    def select(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            idx = win32.user32.SendMessageW(self.hwnd, 0x018A, 0, text)  # LB_FINDSTRING
            if idx >= 0:
                win32.user32.SendMessageW(self.hwnd, 0x0186, idx, 0)  # LB_SETCURSEL

    def selected_text(self) -> str:
        if not win32.IS_WINDOWS or not self.hwnd:
            return ""
        idx = win32.user32.SendMessageW(self.hwnd, 0x0188, 0, 0)  # LB_GETCURSEL
        if idx < 0:
            return ""
        length = win32.user32.SendMessageW(self.hwnd, 0x0199, idx, 0)  # LB_GETTEXTLEN
        buf = __import__("ctypes").create_unicode_buffer(length + 1)
        win32.user32.SendMessageW(self.hwnd, 0x0189, idx, buf)  # LB_GETTEXT
        return buf.value

    def handle_command(self, notification: int) -> bool:
        if notification == win32.LBN_SELCHANGE and self._bind_state is not None:
            self._bind_state.set(self.selected_text())
            return True
        return False


def listbox(
    items: Optional[List[str]] = None,
    bind: Optional[State] = None,
    height: int = 120,
) -> ListBox:
    """Create a list box widget."""
    return _finalize(ListBox(items=items, bind=bind, height=height))
