"""nativewin — zero-dependency Windows GUI toolkit (import alias: nw)."""

from __future__ import annotations

__version__ = "0.1.3"
__all__ = [
    "Window",
    "State",
    "BoolState",
    "vstack",
    "hstack",
    "groupbox",
    "label",
    "input",
    "checkbox",
    "radio",
    "button",
    "divider",
    "textarea",
    "listbox",
    "combobox",
    "tray",
    "is_running",
    "get_event",
    "push_event",
]

from nativewin.state.binding import BoolState, State
from nativewin.layout.manager import groupbox, hstack, vstack
from nativewin.widgets.display import divider, label
from nativewin.widgets.input import button, checkbox, input, radio, textarea
from nativewin.widgets.lists import combobox, listbox
from nativewin.window.events import get_event, is_running, push_event
from nativewin.window.form import Window
from nativewin.window.tray import tray
