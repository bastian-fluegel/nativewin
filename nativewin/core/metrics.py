"""Dialog-unit metrics and the system UI font (message font / DEFAULT_GUI_FONT).

Control sizes follow classic Win32 dialog metrics at 96 DPI (button 75x23,
edit 23px high) and scale with the system DPI.
"""

from __future__ import annotations

import atexit
import ctypes
from typing import Optional, Tuple

from nativewin.core import win32

_font: Optional[int] = None
_font_owned = False
_dpi: Optional[float] = None


def dpi_scale() -> float:
    """Return system DPI / 96. Falls back to 1.0 off Windows."""
    global _dpi
    if _dpi is not None:
        return _dpi
    if not win32.IS_WINDOWS:
        _dpi = 1.0
        return _dpi
    hdc = win32.user32.GetDC(None)
    try:
        raw = win32.gdi32.GetDeviceCaps(hdc, win32.LOGPIXELSX)
        _dpi = (raw / 96.0) if raw else 1.0
    finally:
        win32.user32.ReleaseDC(None, hdc)
    return _dpi


def px(value_at_96: float) -> int:
    """Scale a 96-DPI pixel value to the current system DPI."""
    return max(1, int(round(value_at_96 * dpi_scale())))


def ui_font() -> int:
    """Return an HFONT for dialog/message text. Owned font is released at exit."""
    global _font, _font_owned
    if _font:
        return _font
    if not win32.IS_WINDOWS:
        _font = 0
        return _font

    ncm = win32.NONCLIENTMETRICSW()
    ncm.cbSize = ctypes.sizeof(win32.NONCLIENTMETRICSW)
    if win32.user32.SystemParametersInfoW(
        win32.SPI_GETNONCLIENTMETRICS,
        ncm.cbSize,
        ctypes.byref(ncm),
        0,
    ):
        handle = win32.gdi32.CreateFontIndirectW(ctypes.byref(ncm.lfMessageFont))
        if handle:
            _font = handle
            _font_owned = True
            atexit.register(_release_font)
            return _font

    stock = win32.gdi32.GetStockObject(win32.DEFAULT_GUI_FONT)
    _font = stock
    _font_owned = False
    return _font


def _release_font() -> None:
    global _font
    if _font_owned and _font:
        win32.gdi32.DeleteObject(_font)
        _font = None


def text_size(text: str) -> Tuple[int, int]:
    """Return (width, height) of `text` in the UI font."""
    if not win32.IS_WINDOWS:
        return max(1, len(text) * 7), 15
    sample = text if text else "Ay"
    hdc = win32.user32.GetDC(None)
    previous = win32.gdi32.SelectObject(hdc, ui_font())
    try:
        size = win32.SIZE()
        win32.gdi32.GetTextExtentPoint32W(hdc, sample, len(sample), ctypes.byref(size))
        width = size.cx if text else 0
        return int(width), int(size.cy)
    finally:
        win32.gdi32.SelectObject(hdc, previous)
        win32.user32.ReleaseDC(None, hdc)


def text_width(text: str) -> int:
    return text_size(text)[0]


def text_height() -> int:
    return text_size("Ay")[1]


def apply_ui_font(hwnd: win32.HWND) -> None:
    """Send WM_SETFONT so the control uses the dialog font instead of SYSTEM."""
    if not win32.IS_WINDOWS or not hwnd:
        return
    win32.user32.SendMessageW(hwnd, win32.WM_SETFONT, ui_font(), 1)


def button_size(label: str) -> Tuple[int, int]:
    """Standard dialog push-button size (min 75x23 @ 96 DPI)."""
    width = max(px(75), text_width(label) + px(16))
    return width, px(23)


def edit_height() -> int:
    return px(23)


def label_height() -> int:
    return max(px(13), text_height())


def check_height() -> int:
    return max(px(16), text_height())


def check_width(label: str) -> int:
    """Checkbox/radio width: box + gap + label."""
    return px(13) + px(6) + text_width(label)


def divider_height() -> int:
    return px(2)


def combo_closed_height() -> int:
    return px(23)


def combo_item_height() -> int:
    return max(px(13), text_height())


def combo_create_height() -> int:
    """CreateWindow height for ComboBox includes the dropped list."""
    return combo_closed_height() + combo_item_height() * 8


def edit_min_width() -> int:
    return px(40)


def dialog_padding() -> int:
    return px(11)


def dialog_spacing() -> int:
    return px(7)


def group_padding() -> int:
    return px(10)


def group_title_band() -> int:
    return text_height() + px(2)


def scroll_line() -> int:
    return max(px(16), text_height())


def scrollbar_width() -> int:
    if not win32.IS_WINDOWS:
        return px(17)
    return int(win32.user32.GetSystemMetrics(win32.SM_CXVSCROLL))


def scrollbar_height() -> int:
    if not win32.IS_WINDOWS:
        return px(17)
    return int(win32.user32.GetSystemMetrics(win32.SM_CYHSCROLL))
