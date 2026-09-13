# Overview

**nativewin** (`import nativewin as nw`) is a Windows GUI toolkit written in pure Python using `ctypes`.

## Features

| Feature | API |
|---------|-----|
| Window | `nw.Window(title, width, height)` |
| Reactive state | `nw.State("value")` |
| Vertical layout | `with nw.vstack(padding=16):` |
| Horizontal layout | `with nw.hstack():` |
| Group box | `with nw.groupbox("Title"):` |
| Controls | `label`, `input`, `checkbox`, `button`, `divider`, `textarea`, `listbox` |
| Event loop | `nw.get_event()`, `nw.is_running(win)` |
| System tray | `nw.tray(icon="info", tooltip="...")` |

## Layer responsibilities

- **core/** — Win32 constants, function prototypes, DPI bootstrap, GDI+ image loading.
- **state/** — Observer-based `State` for widget binding.
- **layout/** — Slot calculators and scroll/wheel forwarding.
- **widgets/** — Thin Win32 control wrappers.
- **window/** — `HWND` lifecycle, WNDPROC dispatch, tray integration.

## Win32 invariants

- Pointer-sized handles (`LRESULT`, `WPARAM`, `LPARAM`).
- WNDPROC stored on `Window` instance to prevent GC crashes.
- ComCtl v6 activation context retained until process exit.
- Group boxes use `WS_CLIPSIBLINGS` and `SetWindowTheme("", "")` to avoid scroll smear.

## Running the demo

```bash
python demo.py
```

Requires Windows 10+ with Python 3.10+.
