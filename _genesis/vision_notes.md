# Vision Notes (Genesis)

## Mission

Build a **zero-dependency** Windows GUI toolkit that feels as ergonomic as SwiftUI layout and as straightforward as AutoIt3's linear event loop — while staying close to raw Win32 performance.

## Design pillars

1. **No pip deps** — Python stdlib + native DLLs only (`user32`, `gdi32`, `comctl32`, `shell32`, `gdiplus`).
2. **Declarative layout** — `with nw.vstack():` context managers compute slots; no manual `MoveWindow` in app code.
3. **Linear events** — `while nw.is_running(win): ev = nw.get_event()` instead of nested callbacks.
4. **Reactive state** — `nw.State` two-way binding for inputs and checkboxes.
5. **Layered architecture** — strict top-down deps: `window → widgets → layout → state → core`.

## Non-goals (v0.1)

- Cross-platform rendering (Linux/macOS are import-only for CI).
- Custom widget theming beyond Win32 native + ComCtl v6.
- Web-based or GPU-accelerated UI.

## Future direction

- Additional widgets (combo box, trackbar, tab control, menu bar).
- Layout modifiers (padding, alignment, min/max sizes).
- Headless smoke tests runnable in CI on Linux (import + layout math).
- Installer / `pyproject.toml` publishing to PyPI.
