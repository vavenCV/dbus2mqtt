import fnmatch

from typing import Any

from dbus2mqtt.dbus.dbus_client import DbusClient


class DbusContext:

    def __init__(self, dbus_client: DbusClient):
        self.dbus_client = dbus_client

    def async_dbus_list_fn(self, bus_name_pattern: str):

        res = []

        self.dbus_client.subscriptions
        for bus_name in self.dbus_client.subscriptions.keys():
            if fnmatch.fnmatchcase(bus_name, bus_name_pattern):
                res.append(bus_name)

        return res

    async def async_dbus_call_fn(self, bus_name: str, path: str, interface: str, method:str, method_args: list[Any]):

        if not isinstance(method_args, list):
            raise ValueError("method_args must be a list")

        proxy_object = self.dbus_client.get_proxy_object(bus_name, path)
        if not proxy_object:
            raise ValueError(f"No matching subscription found for bus_name: {bus_name}, path: {path}")

        obj_interface = proxy_object.get_interface(interface)

        return await self.dbus_client.call_dbus_interface_method(obj_interface, method, method_args)

def jinja_custom_dbus_functions(dbus_client: DbusClient) -> dict[str, Any]:

    dbus_context = DbusContext(dbus_client)

    custom_functions: dict[str, Any] = {}
    custom_functions.update({
        "dbus_list": dbus_context.async_dbus_list_fn,
        "dbus_call": dbus_context.async_dbus_call_fn,
    })

    return custom_functions
