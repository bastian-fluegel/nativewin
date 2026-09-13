#!/usr/bin/env python3
"""nativewin demo — System Control panel matching the target developer experience."""

from __future__ import annotations

import nativewin as nw


def main() -> None:
    win = nw.Window("System Control", width=380, height=420)
    status = nw.State("Standby")
    server_name = nw.State("srv-dc-01")

    with nw.vstack(padding=16, spacing=10):
        nw.label("Target Host:")
        nw.input(bind=server_name)

        with nw.groupbox("Maintenance"):
            chk_force = nw.checkbox("Force Restart")
            btn_action = nw.button("Execute Action")

        nw.divider()
        nw.label("Current Status:")
        nw.input(bind=status, readonly=True)
        log = nw.textarea(readonly=True, height=80)

    tray = nw.tray(icon="info", tooltip="NativeWin Monitor")
    tray.add_menu_item("Show Window", lambda: win.show())
    tray.add_menu_item("---")
    tray.add_menu_item("Exit", lambda: win.close())
    win.add_tray(tray)

    while nw.is_running(win):
        ev = nw.get_event()
        if ev == btn_action:
            log.append_line(f"Starting job on {server_name.value}...")
            status.set("Processing")

    win.destroy()


if __name__ == "__main__":
    main()
