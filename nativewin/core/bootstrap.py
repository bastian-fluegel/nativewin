"""Process bootstrap: DPI awareness and ComCtl32 v6 activation context.

The activation context and its temporary manifest file are retained until
process exit via atexit.register to prevent premature GC / file deletion.
"""

from __future__ import annotations

import atexit
import ctypes
import os
import tempfile
from typing import Optional

from nativewin.core import win32

_MANIFEST_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"/>
    </dependentAssembly>
  </dependency>
</assembly>
"""

_actctx_handle: Optional[int] = None
_manifest_path: Optional[str] = None
_cookie: Optional[int] = None
_initialized = False


def _cleanup_actctx() -> None:
    """Release activation context and remove temporary manifest on exit."""
    global _actctx_handle, _manifest_path, _cookie

    if not win32.IS_WINDOWS:
        return

    if _cookie is not None and _actctx_handle is not None:
        win32.kernel32.DeactivateActCtx(0, _cookie)
        _cookie = None

    if _actctx_handle is not None:
        win32.kernel32.ReleaseActCtx(_actctx_handle)
        _actctx_handle = None

    if _manifest_path and os.path.exists(_manifest_path):
        try:
            os.remove(_manifest_path)
        except OSError:
            pass
    _manifest_path = None


def _enable_dpi_awareness() -> None:
    """Set per-monitor DPI awareness when available."""
    if not win32.IS_WINDOWS:
        return

    try:
        # Windows 10 1703+: DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 (user32)
        win32.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError):
        try:
            shcore = ctypes.windll.shcore
            shcore.SetProcessDpiAwareness(win32.PROCESS_PER_MONITOR_DPI_AWARE)
        except (AttributeError, OSError):
            try:
                win32.user32.SetProcessDPIAware()
            except AttributeError:
                pass


def _enable_comctl_v6() -> None:
    """Activate ComCtl32 v6 via embedded manifest activation context."""
    global _actctx_handle, _manifest_path, _cookie

    if not win32.IS_WINDOWS:
        return

    fd, path = tempfile.mkstemp(suffix=".manifest")
    os.write(fd, _MANIFEST_XML.encode("utf-8"))
    os.close(fd)
    _manifest_path = path

    actctx = win32.ACTCTXW()
    actctx.cbSize = ctypes.sizeof(win32.ACTCTXW)
    actctx.dwFlags = win32.ACTCTX_FLAG_ASSEMBLY_DIRECTORY_VALID
    actctx.lpSource = path
    actctx.lpAssemblyDirectory = os.path.dirname(path)

    handle = win32.kernel32.CreateActCtxW(ctypes.byref(actctx))
    if handle in (-1, 0):
        return

    _actctx_handle = handle
    cookie = win32.ULONG_PTR()
    if win32.kernel32.ActivateActCtx(handle, ctypes.byref(cookie)):
        _cookie = int(cookie.value)


def initialize() -> None:
    """Bootstrap nativewin process environment (idempotent)."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    if not win32.IS_WINDOWS:
        return

    atexit.register(_cleanup_actctx)
    _enable_dpi_awareness()
    _enable_comctl_v6()


if win32.IS_WINDOWS:
    initialize()
