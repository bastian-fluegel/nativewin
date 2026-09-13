"""Linear event loop helpers: get_event and is_running."""

from __future__ import annotations

import queue
from typing import Any, Optional, TYPE_CHECKING, Union

from nativewin.core import win32

if TYPE_CHECKING:
    from nativewin.window.form import Window
    from nativewin.widgets.base import Widget

# Global event queue fed by WNDPROC
_event_queue: queue.Queue[Any] = queue.Queue()
_active_window: Optional["Window"] = None


def set_active_window(window: "Window") -> None:
    global _active_window
    _active_window = window


def get_active_window() -> Optional["Window"]:
    return _active_window


def push_event(event: Any) -> None:
    """Enqueue an application-level event (widget reference, str, etc.)."""
    _event_queue.put(event)


def _window_stopped() -> bool:
    window = _active_window
    if window is None:
        return False
    if not window.running:
        return True
    if win32.IS_WINDOWS and window.hwnd and not win32.user32.IsWindow(window.hwnd):
        window.running = False
        return True
    return False


def get_event(block: bool = True, timeout: Optional[float] = None) -> Any:
    """Return the next queued event after pumping Win32 messages.

    Blocks until an event is available unless block=False.
    Returns None when the active window has been closed (so the caller
    can leave ``while nw.is_running(win)`` instead of hanging on GetMessage).
    """
    if win32.IS_WINDOWS:
        _pump_messages(block=False)
    if _window_stopped():
        return None

    if not block:
        try:
            return _event_queue.get_nowait()
        except queue.Empty:
            if win32.IS_WINDOWS:
                if _window_stopped():
                    return None
                _pump_messages(block=True, timeout=timeout)
                if _window_stopped():
                    return None
                try:
                    return _event_queue.get_nowait()
                except queue.Empty:
                    return None
            return None

    while True:
        if _window_stopped():
            return None
        if win32.IS_WINDOWS:
            _pump_messages(block=True, timeout=timeout)
        if _window_stopped():
            return None
        try:
            return _event_queue.get_nowait()
        except queue.Empty:
            if not win32.IS_WINDOWS:
                import time

                time.sleep(0.05)


def is_running(window: "Window") -> bool:
    """Return True while the window message loop should continue."""
    if not window.running:
        return False
    if not win32.IS_WINDOWS:
        return False
    if not window.hwnd:
        return False
    return bool(win32.user32.IsWindow(window.hwnd))


def _pump_messages(block: bool = False, timeout: Optional[float] = None) -> None:
    msg = win32.MSG()
    if block:
        result = win32.user32.GetMessageW(__import__("ctypes").byref(msg), None, 0, 0)
        if result <= 0:
            if _active_window:
                _active_window.running = False
            return
        _dispatch_message(msg)
    else:
        PM_REMOVE = 0x0001
        while win32.user32.PeekMessageW(
            __import__("ctypes").byref(msg), None, 0, 0, PM_REMOVE
        ):
            if msg.message == win32.WM_QUIT:
                if _active_window:
                    _active_window.running = False
                return
            _dispatch_message(msg)


def _dispatch_message(msg: win32.MSG) -> None:
    """Translate/dispatch one message, forwarding wheel events when needed."""
    if msg.message == win32.WM_MOUSEWHEEL and _active_window and _active_window.hwnd:
        child = msg.hwnd
        if child and child != _active_window.hwnd:
            from nativewin.layout.scroll import forward_wheel_to_parent

            if forward_wheel_to_parent(child, int(msg.wParam), int(msg.lParam)):
                return

    __import__("ctypes")  # ensure ctypes available
    import ctypes

    win32.user32.TranslateMessage(ctypes.byref(msg))
    win32.user32.DispatchMessageW(ctypes.byref(msg))
