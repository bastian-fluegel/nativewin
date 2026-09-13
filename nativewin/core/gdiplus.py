"""GDI+ wrappers for image loading and HICON creation."""

from __future__ import annotations

import ctypes
import os
import sys
from typing import Optional, Tuple

from nativewin.core import win32

if win32.IS_WINDOWS:
    gdiplus = ctypes.windll.gdiplus
else:
    gdiplus = None  # type: ignore[assignment]

# GDI+ token and status codes
Ok = 0
PixelFormat32bppARGB = 0x26200A
UnitPixel = 2
ICON_SMALL = 0
ICON_BIG = 1
LR_DEFAULTSIZE = 0x0040
IMAGE_ICON = 1

# GUID for GdiplusStartupInput
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class GdiplusStartupInput(ctypes.Structure):
    _fields_ = [
        ("GdiplusVersion", ctypes.c_uint32),
        ("DebugEventCallback", ctypes.c_void_p),
        ("SuppressBackgroundThread", ctypes.c_bool),
        ("SuppressExternalCodecs", ctypes.c_bool),
    ]


class GdiplusStartupOutput(ctypes.Structure):
    _fields_ = [
        ("NotificationHook", ctypes.c_void_p),
        ("NotificationUnhook", ctypes.c_void_p),
    ]


_token: Optional[int] = None
_initialized = False


def _setup_prototypes() -> None:
    if not win32.IS_WINDOWS or gdiplus is None:
        return

    gdiplus.GdiplusStartup.restype = ctypes.c_int
    gdiplus.GdiplusStartup.argtypes = [
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(GdiplusStartupInput),
        ctypes.POINTER(GdiplusStartupOutput),
    ]

    gdiplus.GdiplusShutdown.restype = None
    gdiplus.GdiplusShutdown.argtypes = [ctypes.c_ulong]

    gdiplus.GdipCreateBitmapFromFile.restype = ctypes.c_int
    gdiplus.GdipCreateBitmapFromFile.argtypes = [
        ctypes.wintypes.LPCWSTR,
        ctypes.POINTER(ctypes.c_void_p),
    ]

    gdiplus.GdipDisposeImage.restype = ctypes.c_int
    gdiplus.GdipDisposeImage.argtypes = [ctypes.c_void_p]

    gdiplus.GdipGetImageWidth.restype = ctypes.c_int
    gdiplus.GdipGetImageWidth.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
    ]

    gdiplus.GdipGetImageHeight.restype = ctypes.c_int
    gdiplus.GdipGetImageHeight.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
    ]

    gdiplus.GdipCreateHICONFromBitmap.restype = ctypes.c_int
    gdiplus.GdipCreateHICONFromBitmap.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(win32.HICON),
    ]


_setup_prototypes()


def startup() -> None:
    """Initialize GDI+ subsystem (idempotent)."""
    global _token, _initialized
    if _initialized or not win32.IS_WINDOWS:
        return

    win32.require_windows()
    token = ctypes.c_ulong()
    inp = GdiplusStartupInput()
    inp.GdiplusVersion = 1
    status = gdiplus.GdiplusStartup(ctypes.byref(token), ctypes.byref(inp), None)
    if status != Ok:
        raise RuntimeError(f"GdiplusStartup failed with status {status}")
    _token = token.value
    _initialized = True


def shutdown() -> None:
    """Shut down GDI+ and release token."""
    global _token, _initialized
    if not _initialized or _token is None or not win32.IS_WINDOWS:
        return
    gdiplus.GdiplusShutdown(_token)
    _token = None
    _initialized = False


def load_icon_from_file(path: str, size: Tuple[int, int] = (32, 32)) -> win32.HICON:
    """Load PNG/JPG/BMP image file and return a 32-bit ARGB HICON."""
    win32.require_windows()
    startup()

    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Icon file not found: {abs_path}")

    ext = os.path.splitext(abs_path)[1].lower()
    if ext in (".ico",):
        handle = win32.user32.LoadImageW(
            None,
            abs_path,
            IMAGE_ICON,
            size[0],
            size[1],
            win32.LR_LOADFROMFILE if hasattr(win32, "LR_LOADFROMFILE") else 0x0010,
        )
        return win32.HICON(handle)

    bitmap = ctypes.c_void_p()
    status = gdiplus.GdipCreateBitmapFromFile(abs_path, ctypes.byref(bitmap))
    if status != Ok:
        raise RuntimeError(f"GdipCreateBitmapFromFile failed: {status}")

    try:
        icon = win32.HICON()
        status = gdiplus.GdipCreateHICONFromBitmap(bitmap, ctypes.byref(icon))
        if status != Ok:
            raise RuntimeError(f"GdipCreateHICONFromBitmap failed: {status}")
        return icon
    finally:
        gdiplus.GdipDisposeImage(bitmap)


def load_stock_icon(name: str) -> win32.HICON:
    """Load a stock system icon by symbolic name."""
    win32.require_windows()
    mapping = {
        "application": win32.IDI_APPLICATION,
        "info": win32.IDI_INFORMATION,
        "information": win32.IDI_INFORMATION,
        "warning": win32.IDI_WARNING,
        "error": win32.IDI_ERROR,
    }
    icon_id = mapping.get(name.lower(), win32.IDI_APPLICATION)
    handle = win32.user32.LoadIconW(None, icon_id)
    return win32.HICON(handle)


def destroy_icon(icon: win32.HICON) -> None:
    """Destroy an HICON handle."""
    if not win32.IS_WINDOWS or not icon:
        return
    win32.user32.DestroyIcon(icon)
