"""Main Window class with WNDPROC, layout, and lifecycle."""

from __future__ import annotations

import ctypes
from typing import List, Optional, TYPE_CHECKING

from nativewin.core import bootstrap  # noqa: F401  — side-effect init
from nativewin.core import win32
from nativewin.layout.manager import LayoutContainer, measure_container
from nativewin.layout.scroll import ScrollState, forward_wheel_to_parent
from nativewin.window import events
from nativewin.window.tray import TrayIcon

if TYPE_CHECKING:
    from nativewin.widgets.base import Widget
    from nativewin.widgets.display import GroupBoxWidget


class Window:
    """Top-level Win32 overlapped window hosting declarative layout.

    Parameters
    ----------
    title:
        Window caption text.
    width, height:
        Client area dimensions in pixels.
    """

    _class_registered = False
    _class_name = "NativeWin_Window"

    def __init__(
        self,
        title: str,
        width: int = 400,
        height: int = 300,
    ) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.hwnd: Optional[win32.HWND] = None
        self.running = True
        self._widgets: List["Widget"] = []
        self._root_layout: Optional[LayoutContainer] = None
        self._group_frames: List["GroupBoxWidget"] = []
        self._trays: List[TrayIcon] = []
        self._scroll = ScrollState(self)
        self._wndproc_ref: Optional[win32.WNDPROC] = None  # GC guard
        self._brush = None

        from nativewin.layout.manager import set_active_window

        set_active_window(self)
        events.set_active_window(self)

        if win32.IS_WINDOWS:
            self._register_class()
            self._create_hwnd()

    def _register_class(self) -> None:
        if Window._class_registered:
            return

        self._wndproc_ref = win32.WNDPROC(self._wndproc)

        wc = win32.WNDCLASSW()
        wc.style = win32.CS_HREDRAW | win32.CS_VREDRAW | win32.CS_DBLCLKS
        wc.lpfnWndProc = self._wndproc_ref
        wc.hInstance = win32.kernel32.GetModuleHandleW(None)
        wc.hCursor = win32.user32.LoadCursorW(None, win32.IDC_ARROW)
        wc.hbrBackground = win32.gdi32.CreateSolidBrush(0x00FFFFFF)  # white
        wc.lpszClassName = self._class_name
        self._brush = wc.hbrBackground

        win32.user32.RegisterClassW(ctypes.byref(wc))
        Window._class_registered = True

    def _create_hwnd(self) -> None:
        hwnd = win32.user32.CreateWindowExW(
            0,
            self._class_name,
            self.title,
            win32.WS_OVERLAPPEDWINDOW | win32.WS_CLIPCHILDREN,
            win32.CW_USEDEFAULT,
            win32.CW_USEDEFAULT,
            self.width,
            self.height,
            None,
            None,
            win32.kernel32.GetModuleHandleW(None),
            None,
        )
        self.hwnd = hwnd
        win32.user32.SetWindowLongPtrW(
            hwnd,
            win32.GWL_USERDATA,
            id(self),
        )
        win32.user32.ShowWindow(hwnd, win32.SW_SHOW)
        win32.user32.UpdateWindow(hwnd)

    def _wndproc(
        self,
        hwnd: win32.HWND,
        msg: int,
        wparam: win32.WPARAM,
        lparam: win32.LPARAM,
    ) -> win32.LRESULT:
        if msg == win32.WM_CREATE:
            return 0

        if msg == win32.WM_SIZE:
            self.relayout()
            return 0

        if msg == win32.WM_MOUSEWHEEL:
            from nativewin.layout.scroll import wheel_delta

            self._scroll.apply_wheel(wheel_delta(int(wparam)))
            return 0

        if msg == win32.WM_COMMAND:
            ctrl_id = wparam & 0xFFFF
            notification = (wparam >> 16) & 0xFFFF
            for widget in self._widgets:
                if widget.control_id == ctrl_id:
                    if widget.handle_command(notification):
                        events.push_event(widget)
                    break
            return 0

        if msg == win32.WM_TRAYICON:
            if lparam == 0x0204:  # WM_RBUTTONUP
                for tray in self._trays:
                    tray.show_context_menu()
            elif lparam == 0x0203:  # WM_LBUTTONDBLCLK
                self.show()
            return 0

        if msg == win32.WM_CLOSE:
            self.running = False
            win32.user32.PostQuitMessage(0)
            return 0

        if msg == win32.WM_DESTROY:
            self.running = False
            return 0

        return win32.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    @staticmethod
    def _from_hwnd(hwnd: win32.HWND) -> Optional["Window"]:
        data = win32.user32.GetWindowLongPtrW(hwnd, win32.GWL_USERDATA)
        if not data:
            return None
        # USERDATA stores id(self); lookup via active window as fallback
        return events.get_active_window()

    def register_widget(self, widget: "Widget") -> None:
        self._widgets.append(widget)

    def set_root_layout(self, layout: LayoutContainer) -> None:
        self._root_layout = layout
        self._build_controls()
        self.relayout()

    def _build_controls(self) -> None:
        if not win32.IS_WINDOWS or not self.hwnd or not self._root_layout:
            return

        self._create_layout_widgets(self._root_layout, self.hwnd)

    def _create_layout_widgets(
        self,
        container: LayoutContainer,
        parent_hwnd: win32.HWND,
    ) -> None:
        from nativewin.widgets.display import GroupBoxWidget

        if container.kind == "groupbox":
            frame = GroupBoxWidget(container.title, height=100)
            frame.create(self, parent_hwnd)
            self._group_frames.append(frame)
            container._frame = frame  # noqa: SLF001
            inner_parent = frame.hwnd or parent_hwnd
            for child in container.children:
                if isinstance(child, LayoutContainer):
                    self._create_layout_widgets(child, inner_parent)
                else:
                    child.create(self, inner_parent)
        else:
            for child in container.children:
                if isinstance(child, LayoutContainer):
                    if child.kind == "groupbox":
                        self._create_layout_widgets(child, parent_hwnd)
                    else:
                        self._create_layout_widgets(child, parent_hwnd)
                else:
                    child.create(self, parent_hwnd)

    def relayout(self) -> None:
        if not self._root_layout or not win32.IS_WINDOWS:
            return

        rect = win32.RECT()
        win32.user32.GetClientRect(self.hwnd, ctypes.byref(rect))
        client_w = rect.width
        client_h = rect.height

        measure_container(self._root_layout, client_w, client_h)
        self._scroll.content_height = getattr(
            self._root_layout, "measured_height", client_h
        )
        self._scroll.viewport_height = client_h
        self._scroll.clamp()

        self._position_layout(self._root_layout, self._scroll.offset_y)

        for frame in self._group_frames:
            frame._apply_theme()

    def _position_layout(
        self,
        container: LayoutContainer,
        scroll_offset: int,
    ) -> None:
        from nativewin.layout.manager import LayoutSlot

        if container.kind == "groupbox" and hasattr(container, "_frame"):
            frame = container._frame
            mh = getattr(container, "measured_height", 100)
            frame._frame_height = mh  # noqa: SLF001
            if hasattr(container, "_slot"):
                frame._slot = LayoutSlot(  # noqa: SLF001
                    container._slot.x,  # noqa: SLF001
                    container._slot.y,  # noqa: SLF001
                    container._slot.width,  # noqa: SLF001
                    mh,
                )
            frame.move_to_slot(scroll_offset)

        for child in container.children:
            if isinstance(child, LayoutContainer):
                self._position_layout(child, scroll_offset)
            else:
                child.move_to_slot(scroll_offset)

    def add_tray(self, tray: TrayIcon) -> None:
        tray.window = self
        self._trays.append(tray)
        tray.create()

    def show(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.ShowWindow(self.hwnd, win32.SW_SHOW)
            win32.user32.SetForegroundWindow(self.hwnd)

    def hide(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.ShowWindow(self.hwnd, win32.SW_HIDE)

    def close(self) -> None:
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.PostMessageW(self.hwnd, win32.WM_CLOSE, 0, 0)

    def destroy(self) -> None:
        for tray in list(self._trays):
            tray.destroy()
        for widget in self._widgets:
            widget.destroy()
        if win32.IS_WINDOWS and self.hwnd:
            win32.user32.DestroyWindow(self.hwnd)
            self.hwnd = None
        if self._brush and win32.IS_WINDOWS:
            win32.gdi32.DeleteObject(self._brush)
            self._brush = None

    def __enter__(self) -> "Window":
        return self

    def __exit__(self, *args) -> None:
        self.destroy()
