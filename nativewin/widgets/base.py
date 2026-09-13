"""Base widget class and shared Win32 control helpers."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from nativewin.core import metrics, win32
from nativewin.layout.manager import LayoutSlot, register_widget

if TYPE_CHECKING:
    from nativewin.window.form import Window

_control_id_counter = 1000


def _next_control_id() -> int:
    global _control_id_counter
    _control_id_counter += 1
    return _control_id_counter


class Widget:
    """Base class for all nativewin controls."""

    _class_name: str = "STATIC"
    _window_style: int = win32.WS_CHILD | win32.WS_VISIBLE | win32.WS_CLIPSIBLINGS
    _window_ex_style: int = 0
    fills_width: bool = True

    def __init__(self) -> None:
        self.hwnd: Optional[win32.HWND] = None
        self.control_id: int = _next_control_id()
        self._slot: LayoutSlot = LayoutSlot()
        self._container = None
        self._window: Optional["Window"] = None
        self._visible = True

    def min_width(self) -> int:
        return metrics.px(20)

    def intrinsic_width(self) -> int:
        return self.min_width()

    def preferred_width(self, available: int) -> int:
        """Width used by layout. Stretch widgets grow; others keep intrinsic size."""
        if self.fills_width:
            return max(self.min_width(), available)
        return self.intrinsic_width()

    def preferred_height(self, width: int) -> int:
        """Return preferred height in pixels for layout."""
        return metrics.edit_height()

    def _create_width(self) -> int:
        return 80

    def _create_height(self) -> int:
        return self.preferred_height(80)

    def create(self, window: "Window", parent_hwnd: win32.HWND) -> None:
        """Create the Win32 child window."""
        self._window = window
        if not win32.IS_WINDOWS:
            return

        text = self._create_text()
        hwnd = win32.user32.CreateWindowExW(
            self._window_ex_style,
            self._class_name,
            text,
            self._window_style,
            0,
            0,
            self._create_width(),
            self._create_height(),
            parent_hwnd,
            self.control_id,
            win32.kernel32.GetModuleHandleW(None),
            None,
        )
        self.hwnd = hwnd
        metrics.apply_ui_font(hwnd)
        self._on_created()

    def _create_text(self) -> str:
        return ""

    def _on_created(self) -> None:
        pass

    def move_to_slot(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """Position control according to computed layout slot."""
        if not win32.IS_WINDOWS or not self.hwnd:
            return
        win32.user32.MoveWindow(
            self.hwnd,
            self._slot.x - offset_x,
            self._slot.y - offset_y,
            max(1, self._slot.width),
            max(1, self._slot.height),
            True,
        )

    def destroy(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.DestroyWindow(self.hwnd)
            self.hwnd = None

    def enable(self, enabled: bool = True) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.EnableWindow(self.hwnd, enabled)

    def show(self, visible: bool = True) -> None:
        self._visible = visible
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.ShowWindow(
                self.hwnd, win32.SW_SHOW if visible else win32.SW_HIDE
            )

    def handle_command(self, notification: int) -> bool:
        """Handle WM_COMMAND notification; return True if consumed."""
        return False

    def handle_notify(self, code: int) -> bool:
        """Handle WM_NOTIFY; return True if consumed."""
        return False

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)


def _resolve_window() -> "Window":
    from nativewin.layout.manager import get_active_window

    return get_active_window()


def _finalize(widget: Widget) -> Widget:
    window = _resolve_window()
    register_widget(widget)
    window.register_widget(widget)
    return widget
