"""nativewin — zero-dependency Windows GUI toolkit (import alias: nw)."""

from __future__ import annotations

__version__ = "0.1.0"
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
    "button",
    "divider",
    "textarea",
    "listbox",
    "tray",
    "is_running",
    "get_event",
    "push_event",
]

from nativewin.state.binding import BoolState, State
from nativewin.layout.manager import groupbox, hstack, vstack
from nativewin.widgets.display import divider, label
from nativewin.widgets.input import button, checkbox, input, textarea
from nativewin.widgets.lists import listbox
from nativewin.window.events import get_event, is_running, push_event
from nativewin.window.form import Window
from nativewin.window.tray import tray
