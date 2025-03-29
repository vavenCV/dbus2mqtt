
from collections.abc import Callable
from typing import Any

import dbus_next.aio as dbus_aio


class DbusSignalHandler:

    handler: Callable[[str, str, str, str, str, dict[str, Any]], None]

    def on_dbus_signal(self, bus_name: str, path: str, interface: str, signal: str, topic: str, msg: dict[str, Any]):
        if self.handler:
            self.handler(bus_name, path, interface, signal, topic, msg)

class BusNameSubscriptions:

    def __init__(self, bus_name: str, signal_handler: DbusSignalHandler):
        self.bus_name = bus_name
        self.signal_handler = signal_handler
        self.path_objects: dict[str, dbus_aio.proxy_object.ProxyObject] = {}


