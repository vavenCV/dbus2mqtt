from unittest.mock import AsyncMock, MagicMock

import pytest

import dbus2mqtt.config as config

from dbus2mqtt.dbus.dbus_types import BusNameSubscriptions
from dbus2mqtt.event_broker import MqttMessage
from tests import mocked_app_context, mocked_dbus_client


@pytest.mark.asyncio
async def test_mqtt_command():

    app_context = mocked_app_context()
    dbus_client = mocked_dbus_client(app_context)

    app_context.config.dbus.subscriptions = [
            config.SubscriptionConfig(
                bus_name="test.bus_name.*",
                path="/path/to/object",
                interfaces=[
                    config.InterfaceConfig(
                        interface="test-interface-name",
                        mqtt_command_topic="dbus2mqtt/test/command",
                        methods=[
                            config.MethodConfig(method="TestMethod1"),
                            config.MethodConfig(method="TestMethod2")
                        ]
                    )
                ]

            )
        ]

    bus_name = "test.bus_name.testapp"
    dbus_client.subscriptions[bus_name] = BusNameSubscriptions(bus_name, ":1:1")

    mocked_proxy_object = MagicMock()
    mocked_proxy_interface = MagicMock()
    mocked_proxy_interface.call_test_method2 = AsyncMock()

    mocked_proxy_object.get_interface.return_value = mocked_proxy_interface

    dbus_client.subscriptions[bus_name].path_objects["/path/to/object"] = mocked_proxy_object

    await dbus_client._on_mqtt_msg(
        MqttMessage(
            topic="dbus2mqtt/test/command",
            payload={
                "method": "TestMethod2",
                "args": {
                    "bus_name": "org.mpris.MediaPlayer2.vlc",
                    "path": "/org/mpris/MediaPlayer2"
                }
            }
        )
    )

    assert mocked_proxy_interface.call_test_method2.call_count == 1
