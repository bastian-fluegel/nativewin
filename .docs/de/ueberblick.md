# Überblick

**nativewin** (`import nativewin as nw`) ist ein Windows-GUI-Toolkit in reinem Python mit `ctypes` — ohne pip-Abhängigkeiten.

## Funktionen

| Funktion | API |
|----------|-----|
| Fenster | `nw.Window(titel, breite, hoehe)` |
| Reaktiver Zustand | `nw.State("wert")` |
| Vertikales Layout | `with nw.vstack(padding=16):` |
| Horizontales Layout | `with nw.hstack():` |
| Gruppierungsrahmen | `with nw.groupbox("Titel"):` |
| Steuerelemente | `label`, `input`, `checkbox`, `button`, `divider`, `textarea`, `listbox` |
| Ereignisschleife | `nw.get_event()`, `nw.is_running(win)` |
| Infobereich (Tray) | `nw.tray(icon="info", tooltip="...")` |

## Schichten

- **core/** — Win32-Konstanten, Prototypen, DPI-Bootstrap, GDI+ Bildladen.
- **state/** — Beobachter-basiertes `State` für Widget-Bindung.
- **layout/** — Slot-Berechnung und Scroll/Rad-Weiterleitung.
- **widgets/** — Win32-Control-Wrapper.
- **window/** — `HWND`-Lebenszyklus, WNDPROC, Tray-Integration.

## Demo starten

```bash
python demo.py
```

Benötigt Windows 10+ und Python 3.10+.
