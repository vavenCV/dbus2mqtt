import fnmatch

from typing import Any

from dbus2mqtt.dbus.dbus_client import DbusClient


class DbusContext:

    def __init__(self, dbus_client: DbusClient):
        self.dbus_client = dbus_client

    # async def async_dbus_call_fn(self, interface: str, method: str, bus_name: str):
    #     obj_interface = proxy_object.get_interface(interface)

    #     call_method_name = "call_" + camel_to_snake(method)
    #     res = await obj_interface.__getattribute__(call_method_name)(bus_name)
    #     return unwrap_dbus_object(res)

    def async_dbus_list_fn(self, bus_name_pattern: str):

        res = []

        self.dbus_client.subscriptions
        for bus_name in self.dbus_client.subscriptions.keys():
            if fnmatch.fnmatchcase(bus_name, bus_name_pattern):
                res.append(bus_name)

        return res

def jinja_custom_dbus_functions(dbus_client: DbusClient) -> dict[str, Any]:

    dbus_context = DbusContext(dbus_client)

    custom_functions: dict[str, Any] = {}
    custom_functions.update({
        "dbus_list": dbus_context.async_dbus_list_fn
    })

    return custom_functions
