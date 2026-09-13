"""Raw Win32 API definitions and ctypes bindings.

All message codes, styles, and notification constants are declared here as
named constants. Handles and message parameters use pointer-sized types.
"""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    gdi32 = ctypes.windll.gdi32
    comctl32 = ctypes.windll.comctl32
    shell32 = ctypes.windll.shell32
    uxtheme = ctypes.windll.uxtheme
else:
    user32 = None  # type: ignore[assignment]
    kernel32 = None  # type: ignore[assignment]
    gdi32 = None  # type: ignore[assignment]
    comctl32 = None  # type: ignore[assignment]
    shell32 = None  # type: ignore[assignment]
    uxtheme = None  # type: ignore[assignment]

# ctypes.wintypes omits several Win32 aliases on all platforms (including Windows).
UINT_PTR = getattr(wintypes, "UINT_PTR", ctypes.c_size_t)
ULONG_PTR = getattr(wintypes, "ULONG_PTR", ctypes.c_size_t)
COLORREF = getattr(wintypes, "COLORREF", wintypes.DWORD)
HRESULT = getattr(wintypes, "HRESULT", ctypes.c_long)
ATOM = getattr(wintypes, "ATOM", wintypes.WORD)
USHORT = getattr(wintypes, "USHORT", wintypes.WORD)

# Pointer-sized aliases -------------------------------------------------------
HWND = wintypes.HWND
HINSTANCE = wintypes.HINSTANCE
HICON = wintypes.HICON
HCURSOR = getattr(wintypes, "HCURSOR", wintypes.HANDLE)
HBRUSH = getattr(wintypes, "HBRUSH", wintypes.HANDLE)
HFONT = getattr(wintypes, "HFONT", wintypes.HANDLE)
HMENU = getattr(wintypes, "HMENU", wintypes.HANDLE)
HDC = getattr(wintypes, "HDC", wintypes.HANDLE)
HBITMAP = getattr(wintypes, "HBITMAP", wintypes.HANDLE)
HPEN = getattr(wintypes, "HPEN", wintypes.HANDLE)
HGDIOBJ = getattr(wintypes, "HGDIOBJ", wintypes.HANDLE)
HMODULE = wintypes.HMODULE
HHOOK = getattr(wintypes, "HHOOK", wintypes.HANDLE)

LRESULT = wintypes.LPARAM
WPARAM = wintypes.WPARAM
LPARAM = wintypes.LPARAM

# ctypes.wintypes has no WNDPROC on Windows or elsewhere.
_FUNCTYPE = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
WNDPROC = _FUNCTYPE(LRESULT, HWND, wintypes.UINT, WPARAM, LPARAM)

# Window messages -------------------------------------------------------------
WM_NULL = 0x0000
WM_CREATE = 0x0001
WM_DESTROY = 0x0002
WM_MOVE = 0x0003
WM_SIZE = 0x0005
WM_SETFOCUS = 0x0007
WM_KILLFOCUS = 0x0008
WM_CLOSE = 0x0010
WM_QUIT = 0x0012
WM_ERASEBKGND = 0x0014
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_COMMAND = 0x0111
WM_SYSCOMMAND = 0x0112
WM_HSCROLL = 0x0114
WM_VSCROLL = 0x0115
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E
WM_NOTIFY = 0x004E
WM_PAINT = 0x000F
WM_CTLCOLORSTATIC = 0x0138
WM_CTLCOLOREDIT = 0x0133
WM_CTLCOLORBTN = 0x0135
WM_CTLCOLORLISTBOX = 0x0134
WM_DRAWITEM = 0x002B
WM_MEASUREITEM = 0x002C
WM_CONTEXTMENU = 0x007B
WM_USER = 0x0400

# System tray -----------------------------------------------------------------
WM_TRAYICON = WM_USER + 1
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIM_SETVERSION = 0x00000004
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIF_SHOWTIP = 0x00000080
NIIF_INFO = 0x00000001
NIIF_WARNING = 0x00000002
NIIF_ERROR = 0x00000003
NID_VERSION_4 = 4
TPM_LEFTALIGN = 0x0000
TPM_RETURNCMD = 0x0100
TPM_RIGHTBUTTON = 0x0002

# Window styles ---------------------------------------------------------------
WS_OVERLAPPED = 0x00000000
WS_POPUP = 0x80000000
WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
WS_DISABLED = 0x08000000
WS_CLIPSIBLINGS = 0x04000000
WS_CLIPCHILDREN = 0x02000000
WS_VSCROLL = 0x00200000
WS_HSCROLL = 0x00100000
WS_BORDER = 0x00800000
WS_DLGFRAME = 0x00400000
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_CAPTION = WS_BORDER | WS_DLGFRAME
WS_OVERLAPPEDWINDOW = (
    WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX
)
WS_GROUP = 0x00020000
WS_TABSTOP = 0x00010000

# Static control styles
SS_LEFT = 0x00000000
SS_CENTER = 0x00000001
SS_RIGHT = 0x00000002
SS_ICON = 0x00000003
SS_BLACKRECT = 0x00000004
SS_GRAYRECT = 0x00000005
SS_WHITERECT = 0x00000006
SS_BLACKFRAME = 0x00000007
SS_GRAYFRAME = 0x00000008
SS_WHITEFRAME = 0x00000009
SS_ETCHEDHORZ = 0x00000010
SS_ETCHEDVERT = 0x00000011
SS_ETCHEDFRAME = 0x00000012
SS_NOTIFY = 0x00000100

# Edit control styles
ES_LEFT = 0x0000
ES_CENTER = 0x0001
ES_RIGHT = 0x0002
ES_MULTILINE = 0x0004
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL = 0x0080
ES_WANTRETURN = 0x1000
ES_READONLY = 0x0800
ES_PASSWORD = 0x0020

# Button styles
BS_PUSHBUTTON = 0x00000000
BS_CHECKBOX = 0x00000002
BS_AUTOCHECKBOX = 0x00000003
BS_RADIOBUTTON = 0x00000004
BS_AUTORADIOBUTTON = 0x00000009
BS_GROUPBOX = 0x00000007
BS_DEFPUSHBUTTON = 0x00000001

# Listbox styles
LBS_NOTIFY = 0x00000001
LBS_SORT = 0x00000002
LBS_NOREDRAW = 0x00000004
LBS_MULTIPLESEL = 0x00000008
LBS_OWNERDRAWFIXED = 0x0010
LBS_OWNERDRAWVARIABLE = 0x0020
LBS_HASSTRINGS = 0x00000000
LBS_NOINTEGRALHEIGHT = 0x0100
LBS_DISABLENOSCROLL = 0x1000
LBS_EXTENDEDSEL = 0x0800
LBS_STANDARD = LBS_NOTIFY | LBS_SORT | WS_VSCROLL | WS_BORDER

# Scroll bar commands
SB_LINEUP = 0
SB_LINEDOWN = 1
SB_PAGEUP = 2
SB_PAGEDOWN = 3
SB_THUMBPOSITION = 4
SB_TOP = 6
SB_BOTTOM = 7

# ShowWindow
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOW = 5
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3

# SetWindowPos
HWND_TOP = 0
HWND_BOTTOM = 1
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOREDRAW = 0x0008
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040
SWP_HIDEWINDOW = 0x0080

# Notification codes
BN_CLICKED = 0
BN_DBLCLK = 5
EN_CHANGE = 0x0300
EN_UPDATE = 0x0400
LBN_SELCHANGE = 1
LBN_DBLCLK = 2

# Class styles
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
CS_DBLCLKS = 0x0008

# Extended window styles
WS_EX_CLIENTEDGE = 0x00000200
WS_EX_STATICEDGE = 0x00020000
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
WS_EX_ACCEPTFILES = 0x00000010
WS_EX_TRANSPARENT = 0x00000020

# Colors
COLOR_WINDOW = 5
COLOR_BTNFACE = 15
COLOR_3DFACE = COLOR_BTNFACE

# GDI
TRANSPARENT = 1
SRCCOPY = 0x00CC0020
BI_RGB = 0
DIB_RGB_COLORS = 0

# DPI awareness
PROCESS_PER_MONITOR_DPI_AWARE = 2

# Activation context
ACTCTX_FLAG_ASSEMBLY_DIRECTORY_VALID = 0x00000004
ACTCTX_FLAG_RESOURCE_NAME_VALID = 0x00000008

# Menu flags
MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800
MF_POPUP = 0x00000010
MF_GRAYED = 0x00000001
MF_DISABLED = 0x00000002

# Misc constants
CW_USEDEFAULT = 0x80000000
IDC_ARROW = 32512
IDI_APPLICATION = 32512
IDI_INFORMATION = 32516
IDI_WARNING = 32515
IDI_ERROR = 32513
LR_LOADFROMFILE = 0x0010
GW_CHILD = 5
GW_HWNDNEXT = 2
GWL_STYLE = -16
GWL_EXSTYLE = -20
GWL_WNDPROC = -4
GWL_ID = -12
GWL_USERDATA = -21

# Trackbar (for wheel forwarding exclusion)
TBS_HORZ = 0x0000
TBS_VERT = 0x0002

# Structs ---------------------------------------------------------------------
class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", HWND),
        ("message", wintypes.UINT),
        ("wParam", WPARAM),
        ("lParam", LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", wintypes.BYTE * 32),
    ]


class CREATESTRUCTW(ctypes.Structure):
    _fields_ = [
        ("lpCreateParams", wintypes.LPVOID),
        ("hInstance", HINSTANCE),
        ("hMenu", HMENU),
        ("hwndParent", HWND),
        ("cy", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x", ctypes.c_int),
        ("style", wintypes.LONG),
        ("lpszName", wintypes.LPCWSTR),
        ("lpszClass", wintypes.LPCWSTR),
        ("dwExStyle", wintypes.DWORD),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class NMHDR(ctypes.Structure):
    _fields_ = [
        ("hwndFrom", HWND),
        ("idFrom", UINT_PTR),
        ("code", wintypes.UINT),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", GUID),
        ("hBalloonIcon", HICON),
    ]


class ACTCTXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.ULONG),
        ("dwFlags", wintypes.DWORD),
        ("lpSource", wintypes.LPCWSTR),
        ("wProcessorArchitecture", USHORT),
        ("wLangId", USHORT),
        ("wAssemblyVersion", USHORT * 4),
        ("lpAssemblyDirectory", wintypes.LPCWSTR),
        ("lpResourceName", wintypes.LPCWSTR),
        ("lpApplicationName", wintypes.LPCWSTR),
        ("hModule", HMODULE),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3),
    ]


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", wintypes.BOOL),
        ("xHotspot", wintypes.DWORD),
        ("yHotspot", wintypes.DWORD),
        ("hbmMask", HBITMAP),
        ("hbmColor", HBITMAP),
    ]


# WNDPROC type alias
# (defined above for cross-platform import safety)


def require_windows() -> None:
    """Raise RuntimeError when Win32 APIs are invoked off Windows."""
    if not IS_WINDOWS:
        raise RuntimeError("nativewin requires Windows to run Win32 APIs")


def setup_prototypes() -> None:
    """Configure ctypes function prototypes for pointer safety."""
    if not IS_WINDOWS:
        return

    user32.DefWindowProcW.restype = LRESULT
    user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, WPARAM, LPARAM]

    user32.RegisterClassW.restype = ATOM
    user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]

    user32.CreateWindowExW.restype = HWND
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        HWND,
        HMENU,
        HINSTANCE,
        wintypes.LPVOID,
    ]

    user32.DestroyWindow.restype = wintypes.BOOL
    user32.DestroyWindow.argtypes = [HWND]

    user32.ShowWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [HWND, ctypes.c_int]

    user32.UpdateWindow.restype = wintypes.BOOL
    user32.UpdateWindow.argtypes = [HWND]

    user32.SetWindowPos.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [
        HWND,
        HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]

    user32.MoveWindow.restype = wintypes.BOOL
    user32.MoveWindow.argtypes = [
        HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.BOOL,
    ]

    user32.GetClientRect.restype = wintypes.BOOL
    user32.GetClientRect.argtypes = [HWND, ctypes.POINTER(RECT)]

    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetWindowRect.argtypes = [HWND, ctypes.POINTER(RECT)]

    user32.SetWindowTextW.restype = wintypes.BOOL
    user32.SetWindowTextW.argtypes = [HWND, wintypes.LPCWSTR]

    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [
        HWND,
        wintypes.LPWSTR,
        ctypes.c_int,
    ]

    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextLengthW.argtypes = [HWND]

    user32.SendMessageW.restype = LRESULT
    user32.SendMessageW.argtypes = [HWND, wintypes.UINT, WPARAM, LPARAM]

    user32.PostMessageW.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [HWND, wintypes.UINT, WPARAM, LPARAM]

    user32.GetMessageW.restype = ctypes.c_int
    user32.GetMessageW.argtypes = [
        ctypes.POINTER(MSG),
        HWND,
        wintypes.UINT,
        wintypes.UINT,
    ]

    user32.PeekMessageW.restype = wintypes.BOOL
    user32.PeekMessageW.argtypes = [
        ctypes.POINTER(MSG),
        HWND,
        wintypes.UINT,
        wintypes.UINT,
        wintypes.UINT,
    ]

    user32.TranslateMessage.restype = wintypes.BOOL
    user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]

    user32.DispatchMessageW.restype = LRESULT
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]

    user32.PostQuitMessage.restype = None
    user32.PostQuitMessage.argtypes = [ctypes.c_int]

    user32.SetFocus.restype = HWND
    user32.SetFocus.argtypes = [HWND]

    user32.GetDlgItem.restype = HWND
    user32.GetDlgItem.argtypes = [HWND, ctypes.c_int]

    user32.GetWindowLongPtrW.restype = LRESULT
    user32.GetWindowLongPtrW.argtypes = [HWND, ctypes.c_int]

    user32.SetWindowLongPtrW.restype = LRESULT
    user32.SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, LRESULT]

    user32.CallWindowProcW.restype = LRESULT
    user32.CallWindowProcW.argtypes = [
        WNDPROC,
        HWND,
        wintypes.UINT,
        WPARAM,
        LPARAM,
    ]

    user32.InvalidateRect.restype = wintypes.BOOL
    user32.InvalidateRect.argtypes = [HWND, ctypes.POINTER(RECT), wintypes.BOOL]

    user32.ScreenToClient.restype = wintypes.BOOL
    user32.ScreenToClient.argtypes = [HWND, ctypes.POINTER(POINT)]

    user32.GetWindow.restype = HWND
    user32.GetWindow.argtypes = [HWND, wintypes.UINT]

    user32.GetParent.restype = HWND
    user32.GetParent.argtypes = [HWND]

    user32.SetWindowTheme.restype = HRESULT
    user32.SetWindowTheme.argtypes = [HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]

    user32.LoadIconW.restype = HICON
    user32.LoadIconW.argtypes = [HINSTANCE, wintypes.LPCWSTR]

    user32.LoadCursorW.restype = HCURSOR
    user32.LoadCursorW.argtypes = [HINSTANCE, wintypes.LPCWSTR]

    user32.LoadImageW.restype = wintypes.HANDLE
    user32.LoadImageW.argtypes = [
        HINSTANCE,
        wintypes.LPCWSTR,
        wintypes.UINT,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]

    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]

    user32.EnableWindow.restype = wintypes.BOOL
    user32.EnableWindow.argtypes = [HWND, wintypes.BOOL]

    user32.IsWindow.restype = wintypes.BOOL
    user32.IsWindow.argtypes = [HWND]

    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [HWND]

    user32.GetClassNameW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]

    user32.DestroyIcon.restype = wintypes.BOOL
    user32.DestroyIcon.argtypes = [HICON]

    user32.SetProcessDPIAware.restype = wintypes.BOOL
    user32.SetProcessDPIAware.argtypes = []

    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetWindowThreadProcessId.argtypes = [
        HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]

    user32.TrackPopupMenu.restype = wintypes.BOOL
    user32.TrackPopupMenu.argtypes = [
        HMENU,
        wintypes.UINT,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        HWND,
        ctypes.c_void_p,
    ]

    user32.CreatePopupMenu.restype = HMENU
    user32.CreatePopupMenu.argtypes = []

    user32.AppendMenuW.restype = wintypes.BOOL
    user32.AppendMenuW.argtypes = [
        HMENU,
        wintypes.UINT,
        UINT_PTR,
        wintypes.LPCWSTR,
    ]

    user32.DestroyMenu.restype = wintypes.BOOL
    user32.DestroyMenu.argtypes = [HMENU]

    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [HWND]

    user32.GetCursorPos.restype = wintypes.BOOL
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]

    kernel32.GetModuleHandleW.restype = HINSTANCE
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

    kernel32.SetProcessDpiAwarenessContext.restype = wintypes.BOOL
    kernel32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]

    kernel32.CreateActCtxW.restype = wintypes.HANDLE
    kernel32.CreateActCtxW.argtypes = [ctypes.POINTER(ACTCTXW)]

    kernel32.ActivateActCtx.restype = wintypes.BOOL
    kernel32.ActivateActCtx.argtypes = [wintypes.HANDLE, ctypes.POINTER(ULONG_PTR)]

    kernel32.DeactivateActCtx.restype = wintypes.BOOL
    kernel32.DeactivateActCtx.argtypes = [wintypes.DWORD, ULONG_PTR]

    kernel32.ReleaseActCtx.restype = None
    kernel32.ReleaseActCtx.argtypes = [wintypes.HANDLE]

    gdi32.CreateSolidBrush.restype = HBRUSH
    gdi32.CreateSolidBrush.argtypes = [COLORREF]

    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteObject.argtypes = [HGDIOBJ]

    gdi32.GetStockObject.restype = HGDIOBJ
    gdi32.GetStockObject.argtypes = [ctypes.c_int]

    shell32.Shell_NotifyIconW.restype = wintypes.BOOL
    shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]

    if uxtheme is not None:
        uxtheme.SetWindowTheme.restype = HRESULT
        uxtheme.SetWindowTheme.argtypes = [
            HWND,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
        ]


setup_prototypes()
