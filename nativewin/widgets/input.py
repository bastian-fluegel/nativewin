"""Input widgets: edit, checkbox, button, textarea."""

from __future__ import annotations

from typing import Callable, Optional, Union

from nativewin.core import win32
from nativewin.state.binding import BoolState, State
from nativewin.widgets.base import Widget, _finalize


class EditInput(Widget):
    """Single-line text input with optional State binding."""

    _class_name = "Edit"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_BORDER
        | win32.WS_TABSTOP
        | win32.ES_AUTOHSCROLL
    )

    def __init__(
        self,
        text: str = "",
        bind: Optional[State] = None,
        readonly: bool = False,
        password: bool = False,
    ) -> None:
        super().__init__()
        self._text = text
        self._bind_state = bind
        self._readonly = readonly
        self._password = password
        self._updating = False

    def preferred_height(self, width: int) -> int:
        return 26

    def _on_created(self) -> None:
        if self._readonly:
            style = win32.user32.GetWindowLongPtrW(self.hwnd, win32.GWL_STYLE)
            win32.user32.SetWindowLongPtrW(
                self.hwnd, win32.GWL_STYLE, style | win32.ES_READONLY
            )
        if self._password:
            style = win32.user32.GetWindowLongPtrW(self.hwnd, win32.GWL_STYLE)
            win32.user32.SetWindowLongPtrW(
                self.hwnd, win32.GWL_STYLE, style | win32.ES_PASSWORD
            )
        if self._bind_state is not None:
            self._bind_state.bind(self._on_state_changed)
            self._set_text(self._bind_state.value)
        elif self._text:
            self._set_text(self._text)

    def _on_state_changed(self, value: str) -> None:
        if self._updating:
            return
        self._set_text(value)

    def _set_text(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SetWindowTextW(self.hwnd, text)

    def handle_command(self, notification: int) -> bool:
        if notification in (win32.EN_CHANGE, win32.EN_UPDATE):
            if self._bind_state is not None and self.hwnd:
                length = win32.user32.GetWindowTextLengthW(self.hwnd)
                buf = __import__("ctypes").create_unicode_buffer(length + 1)
                win32.user32.GetWindowTextW(self.hwnd, buf, length + 1)
                self._updating = True
                try:
                    self._bind_state.set(buf.value)
                finally:
                    self._updating = False
            return True
        return False


class TextArea(Widget):
    """Multi-line read/write text area."""

    _class_name = "Edit"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_BORDER
        | win32.WS_TABSTOP
        | win32.ES_MULTILINE
        | win32.ES_AUTOVSCROLL
        | win32.WS_VSCROLL
        | win32.ES_WANTRETURN
    )

    def __init__(
        self,
        text: str = "",
        bind: Optional[State] = None,
        readonly: bool = False,
        height: int = 80,
    ) -> None:
        super().__init__()
        self._text = text
        self._bind_state = bind
        self._readonly = readonly
        self._fixed_height = height
        self._lines: list[str] = []

    def preferred_height(self, width: int) -> int:
        return self._fixed_height

    def _on_created(self) -> None:
        if self._readonly:
            style = win32.user32.GetWindowLongPtrW(self.hwnd, win32.GWL_STYLE)
            win32.user32.SetWindowLongPtrW(
                self.hwnd, win32.GWL_STYLE, style | win32.ES_READONLY
            )
        if self._text:
            self._set_text(self._text)

    def _set_text(self, text: str) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SetWindowTextW(self.hwnd, text)

    def append_line(self, line: str) -> None:
        """Append a line of text to the text area."""
        self._lines.append(line)
        if win32.IS_WINDOWS and self.hwnd:
            current_len = win32.user32.GetWindowTextLengthW(self.hwnd)
            win32.user32.SendMessageW(
                self.hwnd,
                win32.WM_SETTEXT if current_len == 0 else win32.WM_USER + 10,
                0,
                0,
            )
            # Append via EM_REPLACESEL equivalent
            EM_SETSEL = 0x00B1
            EM_REPLACESEL = 0x00C2
            win32.user32.SendMessageW(self.hwnd, EM_SETSEL, current_len, current_len)
            suffix = ("\r\n" if current_len else "") + line
            win32.user32.SendMessageW(self.hwnd, EM_REPLACESEL, 1, suffix)


class CheckBox(Widget):
    """Checkbox control with optional BoolState binding."""

    _class_name = "Button"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.BS_AUTOCHECKBOX
    )

    def __init__(
        self,
        text: str,
        bind: Optional[BoolState] = None,
        checked: bool = False,
    ) -> None:
        super().__init__()
        self._label = text
        self._bind_state = bind
        self._checked = checked

    def _create_text(self) -> str:
        return self._label

    def preferred_height(self, width: int) -> int:
        return 22

    def _on_created(self) -> None:
        if self._bind_state is not None:
            self._bind_state.bind(self._on_state_changed)
            self.set_checked(self._bind_state.value)
        else:
            self.set_checked(self._checked)

    def _on_state_changed(self, value: bool) -> None:
        self.set_checked(value)

    def set_checked(self, checked: bool) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(self.hwnd, 0x00F1, 1 if checked else 0, 0)  # BM_SETCHECK

    def is_checked(self) -> bool:
        if win32.IS_WINDOWS and self.hwnd:
            return bool(win32.user32.SendMessageW(self.hwnd, 0x00F0, 0, 0))  # BM_GETCHECK
        return self._checked

    def handle_command(self, notification: int) -> bool:
        if notification == win32.BN_CLICKED:
            if self._bind_state is not None:
                self._bind_state.set(self.is_checked())
            return True
        return False


class Button(Widget):
    """Push button control."""

    _class_name = "Button"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.BS_PUSHBUTTON
    )

    def __init__(self, text: str, on_click: Optional[Callable[[], None]] = None) -> None:
        super().__init__()
        self._label = text
        self._on_click = on_click

    def _create_text(self) -> str:
        return self._label

    def preferred_height(self, width: int) -> int:
        return 28

    def handle_command(self, notification: int) -> bool:
        if notification == win32.BN_CLICKED and self._on_click:
            self._on_click()
            return True
        return False


def input(
    text: str = "",
    bind: Optional[State] = None,
    readonly: bool = False,
    password: bool = False,
) -> EditInput:
    """Create a single-line input bound to optional State."""
    return _finalize(EditInput(text=text, bind=bind, readonly=readonly, password=password))


def textarea(
    text: str = "",
    bind: Optional[State] = None,
    readonly: bool = False,
    height: int = 80,
) -> TextArea:
    """Create a multi-line text area."""
    return _finalize(TextArea(text=text, bind=bind, readonly=readonly, height=height))


def checkbox(
    text: str,
    bind: Optional[BoolState] = None,
    checked: bool = False,
) -> CheckBox:
    """Create a checkbox control."""
    return _finalize(CheckBox(text=text, bind=bind, checked=checked))


def button(text: str, on_click: Optional[Callable[[], None]] = None) -> Button:
    """Create a push button."""
    return _finalize(Button(text=text, on_click=on_click))
