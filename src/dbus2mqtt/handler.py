from collections.abc import Callable
from typing import Any


class DbusSignalHandler:

    handler: Callable[[str, str, str, str, dict[str, Any]], None]

    def on_dbus_signal(self, bus_name: str, path: str, interface: str, signal: str, msg: dict[str, Any]):
        if self.handler:
            self.handler(bus_name, path, interface, signal, msg)
