"""Input widgets: edit, checkbox, radio, button, textarea."""

from __future__ import annotations

from typing import Callable, Optional

from nativewin.core import metrics, win32
from nativewin.state.binding import BoolState, State
from nativewin.widgets.base import Widget, _finalize

_radio_groups_started: set[int] = set()


class EditInput(Widget):
    """Single-line text input with optional State binding."""

    _class_name = "Edit"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.ES_AUTOHSCROLL
        | win32.ES_LEFT
    )
    _window_ex_style = win32.WS_EX_CLIENTEDGE
    fills_width = True

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

    def min_width(self) -> int:
        return metrics.edit_min_width()

    def preferred_height(self, width: int) -> int:
        return metrics.edit_height()

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
        | win32.WS_TABSTOP
        | win32.ES_MULTILINE
        | win32.ES_AUTOVSCROLL
        | win32.ES_AUTOHSCROLL
        | win32.WS_VSCROLL
        | win32.ES_WANTRETURN
    )
    _window_ex_style = win32.WS_EX_CLIENTEDGE
    fills_width = True

    def __init__(
        self,
        text: str = "",
        bind: Optional[State] = None,
        readonly: bool = False,
        height: int = 64,
    ) -> None:
        super().__init__()
        self._text = text
        self._bind_state = bind
        self._readonly = readonly
        self._fixed_height = height
        self._lines: list[str] = []

    def min_width(self) -> int:
        return metrics.edit_min_width()

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
                self.hwnd, win32.EM_SETSEL, current_len, current_len
            )
            suffix = ("\r\n" if current_len else "") + line
            win32.user32.SendMessageW(self.hwnd, win32.EM_REPLACESEL, 1, suffix)


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
    fills_width = False

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

    def intrinsic_width(self) -> int:
        return metrics.check_width(self._label)

    def preferred_height(self, width: int) -> int:
        return metrics.check_height()

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
            win32.user32.SendMessageW(
                self.hwnd, win32.BM_SETCHECK, 1 if checked else 0, 0
            )

    def is_checked(self) -> bool:
        if win32.IS_WINDOWS and self.hwnd:
            return bool(win32.user32.SendMessageW(self.hwnd, win32.BM_GETCHECK, 0, 0))
        return self._checked

    def handle_command(self, notification: int) -> bool:
        if notification == win32.BN_CLICKED:
            if self._bind_state is not None:
                self._bind_state.set(self.is_checked())
            return True
        return False


class Radio(Widget):
    """Radio button. Radios sharing the same State form one Win32 group."""

    _class_name = "Button"
    fills_width = False

    def __init__(
        self,
        text: str,
        bind: Optional[State] = None,
        checked: bool = False,
        start_group: bool = False,
    ) -> None:
        super().__init__()
        self._label = text
        self._bind_state = bind
        self._checked = checked
        style = (
            win32.WS_CHILD
            | win32.WS_VISIBLE
            | win32.WS_CLIPSIBLINGS
            | win32.WS_TABSTOP
            | win32.BS_AUTORADIOBUTTON
        )
        if start_group:
            style |= win32.WS_GROUP
        self._window_style = style

    def _create_text(self) -> str:
        return self._label

    def intrinsic_width(self) -> int:
        return metrics.check_width(self._label)

    def preferred_height(self, width: int) -> int:
        return metrics.check_height()

    def _on_created(self) -> None:
        if self._bind_state is not None:
            self._bind_state.bind(self._on_state_changed)
            self.set_checked(self._bind_state.value == self._label)
        else:
            self.set_checked(self._checked)

    def _on_state_changed(self, value: str) -> None:
        self.set_checked(value == self._label)

    def set_checked(self, checked: bool) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.SendMessageW(
                self.hwnd, win32.BM_SETCHECK, 1 if checked else 0, 0
            )

    def is_checked(self) -> bool:
        if win32.IS_WINDOWS and self.hwnd:
            return bool(win32.user32.SendMessageW(self.hwnd, win32.BM_GETCHECK, 0, 0))
        return self._checked

    def handle_command(self, notification: int) -> bool:
        if notification == win32.BN_CLICKED:
            if self._bind_state is not None:
                self._bind_state.set(self._label)
            return True
        return False


class Button(Widget):
    """Standard dialog push button (content-sized, not stretched)."""

    _class_name = "Button"
    _window_style = (
        win32.WS_CHILD
        | win32.WS_VISIBLE
        | win32.WS_CLIPSIBLINGS
        | win32.WS_TABSTOP
        | win32.BS_PUSHBUTTON
    )
    fills_width = False

    def __init__(self, text: str, on_click: Optional[Callable[[], None]] = None) -> None:
        super().__init__()
        self._label = text
        self._on_click = on_click

    def _create_text(self) -> str:
        return self._label

    def intrinsic_width(self) -> int:
        return metrics.button_size(self._label)[0]

    def preferred_height(self, width: int) -> int:
        return metrics.button_size(self._label)[1]

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
    height: int = 64,
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


def radio(
    text: str,
    bind: Optional[State] = None,
    checked: bool = False,
) -> Radio:
    """Create a radio button. Shared `bind` State values form one group."""
    start_group = False
    if bind is None:
        start_group = True
    else:
        key = id(bind)
        if key not in _radio_groups_started:
            _radio_groups_started.add(key)
            start_group = True
    return _finalize(Radio(text=text, bind=bind, checked=checked, start_group=start_group))


def button(text: str, on_click: Optional[Callable[[], None]] = None) -> Button:
    """Create a standard dialog push button."""
    return _finalize(Button(text=text, on_click=on_click))
