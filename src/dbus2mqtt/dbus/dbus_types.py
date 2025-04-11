

import dbus_next.aio as dbus_aio


class BusNameSubscriptions:

    def __init__(self, bus_name: str):
        self.bus_name = bus_name
        self.path_objects: dict[str, dbus_aio.proxy_object.ProxyObject] = {}
