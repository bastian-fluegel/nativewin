"""List and selection widgets: list box and combo box."""

from __future__ import annotations

from typing import List, Optional

from nativewin.core import metrics, win32
from nativewin.state.binding import State
from nativewin.widgets.base import Widget, _finalize


class ListBox(Widget):
    """Single-selection list box."""

    _class_name = "ListBox"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.LBS_NOTIFY
        | win32.LBS_NOINTEGRALHEIGHT
        | win32.WS_VSCROLL
    )
    _window_ex_style = win32.WS_EX_CLIENTEDGE
    fills_width = True

    def __init__(
        self,
        items: Optional[List[str]] = None,
        bind: Optional[State] = None,
        height: int = 72,
    ) -> None:
        super().__init__()
        self._items = list(items or [])
        self._bind_state = bind
        self._fixed_height = height

    def min_width(self) -> int:
        return metrics.edit_min_width()

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
            win32.user32.SendMessageW(self.hwnd, win32.LB_ADDSTRING, 0, text)

    def clear(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(self.hwnd, win32.LB_RESETCONTENT, 0, 0)

    def select(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            idx = win32.user32.SendMessageW(self.hwnd, win32.LB_FINDSTRING, 0, text)
            if idx >= 0:
                win32.user32.SendMessageW(self.hwnd, win32.LB_SETCURSEL, idx, 0)

    def selected_text(self) -> str:
        if not win32.IS_WINDOWS or not self.hwnd:
            return ""
        idx = win32.user32.SendMessageW(self.hwnd, win32.LB_GETCURSEL, 0, 0)
        if idx < 0:
            return ""
        length = win32.user32.SendMessageW(self.hwnd, win32.LB_GETTEXTLEN, idx, 0)
        buf = __import__("ctypes").create_unicode_buffer(length + 1)
        win32.user32.SendMessageW(self.hwnd, win32.LB_GETTEXT, idx, buf)
        return buf.value

    def handle_command(self, notification: int) -> bool:
        if notification == win32.LBN_SELCHANGE and self._bind_state is not None:
            self._bind_state.set(self.selected_text())
            return True
        return False


class ComboBox(Widget):
    """Standard drop-down combo box (CBS_DROPDOWNLIST)."""

    _class_name = "ComboBox"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.CBS_DROPDOWNLIST
        | win32.CBS_HASSTRINGS
        | win32.WS_VSCROLL
    )
    fills_width = True

    def __init__(
        self,
        items: Optional[List[str]] = None,
        bind: Optional[State] = None,
    ) -> None:
        super().__init__()
        self._items = list(items or [])
        self._bind_state = bind
        self._dropdown_height = metrics.combo_create_height()

    def min_width(self) -> int:
        widest = metrics.edit_min_width()
        for item in self._items:
            widest = max(widest, metrics.text_width(item) + metrics.px(28))
        return widest

    def preferred_width(self, available: int) -> int:
        return max(self.min_width(), available)

    def preferred_height(self, width: int) -> int:
        return metrics.combo_closed_height()

    def _create_height(self) -> int:
        return self._dropdown_height

    def move_to_slot(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """Keep the dropped-list height; only the closed row is laid out."""
        if not win32.IS_WINDOWS or not self.hwnd:
            return
        win32.user32.MoveWindow(
            self.hwnd,
            self._slot.x - offset_x,
            self._slot.y - offset_y,
            max(1, self._slot.width),
            max(self._slot.height, self._dropdown_height),
            True,
        )

    def _on_created(self) -> None:
        for item in self._items:
            self.add_item(item)
        if self._bind_state is not None:
            self._bind_state.bind(self._on_state_changed)
            if self._bind_state.value:
                self.select(self._bind_state.value)
            elif self._items:
                self.select(self._items[0])
                self._bind_state.set(self._items[0])
        elif self._items:
            self.select(self._items[0])

    def _on_state_changed(self, value: str) -> None:
        self.select(value)

    def add_item(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(self.hwnd, win32.CB_ADDSTRING, 0, text)

    def select(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            idx = win32.user32.SendMessageW(self.hwnd, win32.CB_FINDSTRINGEXACT, -1, text)
            if idx >= 0:
                win32.user32.SendMessageW(self.hwnd, win32.CB_SETCURSEL, idx, 0)

    def selected_text(self) -> str:
        if not win32.IS_WINDOWS or not self.hwnd:
            return ""
        idx = win32.user32.SendMessageW(self.hwnd, win32.CB_GETCURSEL, 0, 0)
        if idx < 0:
            return ""
        length = win32.user32.SendMessageW(self.hwnd, win32.CB_GETLBTEXTLEN, idx, 0)
        buf = __import__("ctypes").create_unicode_buffer(length + 1)
        win32.user32.SendMessageW(self.hwnd, win32.CB_GETLBTEXT, idx, buf)
        return buf.value

    def handle_command(self, notification: int) -> bool:
        if notification == win32.CBN_SELCHANGE and self._bind_state is not None:
            self._bind_state.set(self.selected_text())
            return True
        return False


def listbox(
    items: Optional[List[str]] = None,
    bind: Optional[State] = None,
    height: int = 72,
) -> ListBox:
    """Create a list box widget."""
    return _finalize(ListBox(items=items, bind=bind, height=height))


def combobox(
    items: Optional[List[str]] = None,
    bind: Optional[State] = None,
) -> ComboBox:
    """Create a drop-down combo box."""
    return _finalize(ComboBox(items=items, bind=bind))
