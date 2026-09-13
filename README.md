# nativewin (`nw`)

Zero-dependency Windows GUI toolkit for Python 3.10+. Combines an AutoIt-style linear event loop, SwiftUI-inspired declarative layout, and native Win32 controls via `ctypes` only.

## Requirements

- **Windows 10+** (runtime)
- **Python 3.10+**
- No pip dependencies — stdlib only

## Quick start

```bash
python demo.py
```

## Example

```python
import nativewin as nw

win = nw.Window("System Control", width=320, height=380)
host = nw.State("srv-dc-01")

with nw.vstack():
    nw.label("Target Host:")
    nw.input(bind=host)
    btn = nw.button("Execute")
    log = nw.textarea(readonly=True)

while nw.is_running(win):
    ev = nw.get_event()
    if ev == btn:
        log.append_line(f"Running on {host.value}...")

win.destroy()
```

Standard controls: `label`, `input`, `button`, `checkbox`, `radio`, `combobox`, `listbox`, `textarea`, `divider`, `groupbox`. Window scrollbars appear only when content overflows.

## Architecture

```
nativewin/
├── core/       win32.py, bootstrap.py, metrics.py, gdiplus.py
├── state/      Reactive State binding
├── layout/     vstack / hstack / groupbox managers
├── widgets/    Win32 control wrappers
└── window/     Window, events, system tray
```

## Platform notes

The package can be **imported on non-Windows** platforms for syntax checks and CI. Win32 API calls raise `RuntimeError` or no-op when not on Windows.

## Documentation

- English: [`.docs/en/overview.md`](.docs/en/overview.md)
- Deutsch: [`.docs/de/ueberblick.md`](.docs/de/ueberblick.md)

## License

MIT
