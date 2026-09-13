#!/usr/bin/env python3
"""nativewin demo — compact System Control dialog with standard Win32 controls."""

from __future__ import annotations

import nativewin as nw


def main() -> None:
    win = nw.Window("System Control", width=320, height=380)
    status = nw.State("Standby")
    server_name = nw.State("srv-dc-01")
    action = nw.State("Restart")
    mode = nw.State("Graceful")

    with nw.vstack():
        nw.label("Target Host:")
        nw.input(bind=server_name)

        nw.label("Action:")
        nw.combobox(["Restart", "Shutdown", "Status"], bind=action)

        with nw.groupbox("Maintenance"):
            nw.radio("Graceful", bind=mode)
            nw.radio("Force", bind=mode)
            btn_action = nw.button("Execute")

        nw.divider()
        nw.label("Current Status:")
        nw.input(bind=status, readonly=True)
        log = nw.textarea(readonly=True, height=64)

    tray = nw.tray(icon="info", tooltip="NativeWin Monitor")
    tray.add_menu_item("Show Window", lambda: win.show())
    tray.add_menu_item("---")
    tray.add_menu_item("Exit", lambda: win.close())
    win.add_tray(tray)

    while nw.is_running(win):
        ev = nw.get_event()
        if ev == btn_action:
            log.append_line(f"{action.value} on {server_name.value} ({mode.value})")
            status.set("Processing")

    win.destroy()


if __name__ == "__main__":
    main()
