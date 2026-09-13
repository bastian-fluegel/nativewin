# Changelog

All notable changes to this project are documented in this file.

## [0.1.3] - 2026-09-13

### Fixed

- `get_event()` no longer blocks forever after `WM_QUIT` — closing the window actually leaves the `is_running` loop.
- `WM_CLOSE` destroys the HWND (`DestroyWindow`); `WM_DESTROY` removes the tray icon and posts quit.
- Tray context menu: handle `NOTIFYICON_VERSION_4` (`WM_CONTEXTMENU` / `NIN_*` in `LOWORD(lParam)`), not only classic `WM_RBUTTONUP`.
- `TrackPopupMenu` restype is the command id (`TPM_RETURNCMD`), not `BOOL`.

## [0.1.2] - 2026-09-13

### Added

- Standard dialog controls: `radio`, `combobox` (CBS_DROPDOWNLIST).
- Window H/V scrollbars via `ShowScrollBar` / `SetScrollInfo`, visible only on overflow.
- `WM_HSCROLL`, `WM_VSCROLL`, `WM_MOUSEWHEEL`, and `WM_MOUSEHWHEEL` scrolling.

### Changed

- Controls use the system message font (`WM_SETFONT`) and ComCtl v6 theming — no more SYSTEM-font / unthemed look.
- Dialog metrics at 96 DPI (button 75×23, edit 23px high); buttons, radios, checkboxes, and labels keep intrinsic width instead of stretching.
- Window `width`/`height` are client-area sizes (`AdjustWindowRectEx`).
- Dialog face color (`COLOR_3DFACE`) for the form background and static/button CTLCOLOR.

## [0.1.1] - 2026-09-13

### Fixed

- Define `WNDPROC` via `WINFUNCTYPE` — `ctypes.wintypes` has no `WNDPROC` on Windows, which crashed `import nativewin`.
- Alias other missing `wintypes` names (`USHORT`, `UINT_PTR`, `ULONG_PTR`, `HRESULT`, `ATOM`, `COLORREF`) so ActCtx, menus, and GDI prototypes do not fail next.
- Bind `SetWindowTheme` on `uxtheme` only — it is not exported by `user32` and crashed `setup_prototypes()`.
- Bind `SetProcessDpiAwarenessContext` on `user32` (not `kernel32`).
- Use pointer-sized `ULONG_PTR` for the ActCtx cookie so 64-bit `ActivateActCtx` does not overflow.
- Accept Unicode strings as `SendMessageW` LPARAM so `textarea.append_line()` does not raise `ArgumentError`.

## [0.1.0] - 2026-09-13

### Added

- Initial release of **nativewin** (`nw`) — zero-dependency Win32 GUI toolkit.
- Core layer: `win32.py` (ctypes bindings), `bootstrap.py` (DPI + ComCtl v6), `gdiplus.py` (PNG/JPG → HICON).
- Reactive `State` / `BoolState` binding in `state/binding.py`.
- Declarative layout: `vstack`, `hstack`, `groupbox` context managers with automatic slot positioning.
- Widgets: label, input, checkbox, button, divider, textarea, listbox.
- Window lifecycle with persistent WNDPROC reference (GC-safe).
- Linear event loop: `get_event()`, `is_running()`.
- System tray via `shell32.Shell_NotifyIconW` with context menus.
- Scroll support with `WM_MOUSEWHEEL` forwarding rules.
- `demo.py` — System Control sample application.
- Bilingual docs in `.docs/en/` and `.docs/de/`.
