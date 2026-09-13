"""Display widgets: label, divider, groupbox shell, static image."""

from __future__ import annotations

from typing import Optional

from nativewin.core import win32
from nativewin.widgets.base import Widget, _finalize


class Label(Widget):
    """Static text label."""

    _class_name = "Static"
    _window_style = (
        win32.WS_CHILD | win32.WS_VISIBLE | win32.WS_CLIPSIBLINGS | win32.SS_LEFT
    )

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def _create_text(self) -> str:
        return self._text

    def preferred_height(self, width: int) -> int:
        return 20

    def set_text(self, text: str) -> None:
        self._text = text
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SetWindowTextW(self.hwnd, text)


class Divider(Widget):
    """Horizontal etched divider line."""

    _class_name = "Static"
    _window_style = (
        win32.WS_CHILD | win32.WS_VISIBLE | win32.WS_CLIPSIBLINGS | win32.SS_ETCHEDHORZ
    )

    def preferred_height(self, width: int) -> int:
        return 8


class GroupBoxWidget(Widget):
    """Visual group box frame with title (children laid out separately)."""

    _class_name = "Button"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.BS_GROUPBOX
        | win32.WS_GROUP
    )

    def __init__(self, title: str, height: int = 100) -> None:
        super().__init__()
        self._title = title
        self._frame_height = height

    def _create_text(self) -> str:
        return self._title

    def preferred_height(self, width: int) -> int:
        return self._frame_height

    def _apply_theme(self) -> None:
        super()._apply_theme()
        if win32.IS_WINDOWS and self.hwnd:
            # Prevent border smear during scroll
            win32.user32.SetWindowPos(
                self.hwnd,
                win32.HWND_BOTTOM,
                0,
                0,
                0,
                0,
                win32.SWP_NOMOVE | win32.SWP_NOSIZE | win32.SWP_NOACTIVATE,
            )


class StaticImage(Widget):
    """Static control displaying an icon or bitmap."""

    _class_name = "Static"
    _window_style = (
        win32.WS_CHILD | win32.WS_VISIBLE | win32.WS_CLIPSIBLINGS | win32.SS_ICON
    )

    def __init__(self, icon: win32.HICON, width: int = 32, height: int = 32) -> None:
        super().__init__()
        self._icon = icon
        self._width = width
        self._height = height

    def preferred_height(self, width: int) -> int:
        return self._height

    def _on_created(self) -> None:
        if win32.IS_WINDOWS and self.hwnd and self._icon:
            STM_SETICON = 0x0170
            win32.user32.SendMessageW(self.hwnd, STM_SETICON, self._icon, 0)


def label(text: str) -> Label:
    """Create a text label."""
    return _finalize(Label(text))


def divider() -> Divider:
    """Create a horizontal divider."""
    return _finalize(Divider())
