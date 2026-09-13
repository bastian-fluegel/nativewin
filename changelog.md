# Changelog

All notable changes to this project are documented in this file.

## [0.1.1] - 2026-09-13

### Fixed

- Define `WNDPROC` via `WINFUNCTYPE` — `ctypes.wintypes` has no `WNDPROC` on Windows, which crashed `import nativewin`.
- Alias other missing `wintypes` names (`USHORT`, `UINT_PTR`, `ULONG_PTR`, `HRESULT`, `ATOM`, `COLORREF`) so ActCtx, menus, and GDI prototypes do not fail next.

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
