
import logging

from dbus_next.errors import DBusError

from dbus2mqtt.config import (
    SignalHandlerConfig,
)
from dbus2mqtt.dbus_types import BusNameSubscriptions
from dbus2mqtt.dbus_util import camel_to_snake, unwrap_dbus_object

logger = logging.getLogger(__name__)


async def on_signal(bus_name_subscriptions: BusNameSubscriptions, path: str, interface_name: str, signal_handler_configs: list[SignalHandlerConfig], *args):

    bus_name = bus_name_subscriptions.bus_name
    proxy_object = bus_name_subscriptions.path_objects[path]
    signal_handler = bus_name_subscriptions.signal_handler

    unwrapped_args = [unwrap_dbus_object(o) for o in args]

    for signal_handler_config in signal_handler_configs:
        matches_filter = signal_handler_config.matches_filter(*args)
        if matches_filter:

            async def async_dbus_call_fn(interface: str, method: str, bus_name: str):
                obj_interface = proxy_object.get_interface(interface)

                call_method_name = "call_" + camel_to_snake(method)
                res = await obj_interface.__getattribute__(call_method_name)(bus_name)
                return unwrap_dbus_object(res)

            template_interface_context = {
                "bus_name": bus_name,
                "path": proxy_object.path,
                "interface": interface_name,
            }

            async_template_interface_context = {
                "dbus_call": async_dbus_call_fn
            }

            try:
                payload = await signal_handler_config.render_payload_template(unwrapped_args, context={
                    **template_interface_context, **async_template_interface_context
                })
                mqtt_topic = signal_handler_config.render_mqtt_topic(context=template_interface_context)
            except DBusError as e:
                logger.warning(f"Error rendering jinja template, DBusError: {e.text}")
                return

            log_msg = f"on_signal: signal={signal_handler_config.signal}, bus_name={bus_name}, path={path}, interface={interface_name}"
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"{log_msg}, payload={payload}")
            else:
                logger.info(log_msg)

            signal_handler.on_dbus_signal(bus_name, path, interface_name, signal_handler_config.signal, mqtt_topic, payload)
