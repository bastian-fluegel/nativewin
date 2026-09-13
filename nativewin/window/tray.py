"""System tray icon and context menu support."""

from __future__ import annotations

import ctypes
from typing import Callable, List, Optional, Union

from nativewin.core import win32
from nativewin.core import gdiplus


class TrayMenuItem:
    """Single tray menu entry or separator."""

    def __init__(
        self,
        label: str,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        self.label = label
        self.callback = callback
        self.is_separator = label.strip() == "---"


class TrayIcon:
    """Shell notification area icon with popup menu.

    Parameters
    ----------
    icon:
        Stock icon name ('info', 'warning', 'error') or path to PNG/JPG/ICO.
    tooltip:
        Tooltip text shown on hover.
    window:
        Host window receiving tray callback messages.
    """

    _instances: List["TrayIcon"] = []
    _next_id = 1

    def __init__(
        self,
        icon: str = "info",
        tooltip: str = "",
        window: Optional["Window"] = None,
    ) -> None:
        from nativewin.window.form import Window  # noqa: F401

        self.icon_spec = icon
        self.tooltip = tooltip
        self.window = window
        self.menu_items: List[TrayMenuItem] = []
        self._icon_handle: Optional[win32.HICON] = None
        self._menu: Optional[win32.HMENU] = None
        self._id = TrayIcon._next_id
        TrayIcon._next_id += 1
        TrayIcon._instances.append(self)

    def add_menu_item(
        self,
        label: str,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Append an item or separator ('---') to the context menu."""
        self.menu_items.append(TrayMenuItem(label, callback))

    def create(self) -> None:
        """Register the tray icon with shell32."""
        if not win32.IS_WINDOWS or self.window is None:
            return

        self._icon_handle = self._load_icon()
        nid = win32.NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(win32.NOTIFYICONDATAW)
        nid.hWnd = self.window.hwnd
        nid.uID = self._id
        nid.uFlags = win32.NIF_MESSAGE | win32.NIF_ICON | win32.NIF_TIP | win32.NIF_SHOWTIP
        nid.uCallbackMessage = win32.WM_TRAYICON
        nid.hIcon = self._icon_handle
        nid.szTip = self.tooltip[:127]
        win32.shell32.Shell_NotifyIconW(win32.NIM_ADD, ctypes.byref(nid))

        nid.uVersion = win32.NID_VERSION_4
        win32.shell32.Shell_NotifyIconW(win32.NIM_SETVERSION, ctypes.byref(nid))

    def _load_icon(self) -> win32.HICON:
        if self.icon_spec.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".ico")):
            return gdiplus.load_icon_from_file(self.icon_spec)
        return gdiplus.load_stock_icon(self.icon_spec)

    def show_context_menu(self) -> None:
        """Display popup menu at cursor and dispatch selection."""
        if not win32.IS_WINDOWS or self.window is None:
            return

        menu = win32.user32.CreatePopupMenu()
        self._menu = menu
        cmd_map: dict[int, Callable[[], None]] = {}
        cmd_id = 100

        for item in self.menu_items:
            if item.is_separator:
                win32.user32.AppendMenuW(menu, win32.MF_SEPARATOR, 0, None)
            else:
                win32.user32.AppendMenuW(menu, win32.MF_STRING, cmd_id, item.label)
                if item.callback:
                    cmd_map[cmd_id] = item.callback
                cmd_id += 1

        pt = win32.POINT()
        win32.user32.GetCursorPos(ctypes.byref(pt))
        win32.user32.SetForegroundWindow(self.window.hwnd)
        selected = win32.user32.TrackPopupMenu(
            menu,
            win32.TPM_LEFTALIGN | win32.TPM_RETURNCMD | win32.TPM_RIGHTBUTTON,
            pt.x,
            pt.y,
            0,
            self.window.hwnd,
            None,
        )
        win32.user32.PostMessageW(self.window.hwnd, win32.WM_NULL, 0, 0)
        win32.user32.DestroyMenu(menu)
        self._menu = None

        if selected in cmd_map:
            cmd_map[selected]()

    def destroy(self) -> None:
        """Remove tray icon and free GDI handles."""
        if not win32.IS_WINDOWS or self.window is None:
            return

        nid = win32.NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(win32.NOTIFYICONDATAW)
        nid.hWnd = self.window.hwnd
        nid.uID = self._id
        win32.shell32.Shell_NotifyIconW(win32.NIM_DELETE, ctypes.byref(nid))

        if self._icon_handle and self.icon_spec.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp")
        ):
            gdiplus.destroy_icon(self._icon_handle)
        self._icon_handle = None

        if self in TrayIcon._instances:
            TrayIcon._instances.remove(self)


def tray(
    icon: str = "info",
    tooltip: str = "",
    window: Optional["Window"] = None,
) -> TrayIcon:
    """Create a system tray icon attached to a window."""
    return TrayIcon(icon=icon, tooltip=tooltip, window=window)
