
import asyncio
import json
import logging

from typing import Any

import paho.mqtt.client as mqtt

from paho.mqtt.enums import CallbackAPIVersion

from dbus2mqtt.config import MqttConfig
from dbus2mqtt.dbus_subscription import DbusSignalHandler

logger = logging.getLogger(__name__)

class MqttClient:

    def __init__(self, config: MqttConfig, dbus_signal_handler: DbusSignalHandler):
        self.config = config

        dbus_signal_handler.handler = self.on_dbus_signal

        self.client = mqtt.Client(CallbackAPIVersion.VERSION2)

        self.client.username_pw_set(
            username=config.username,
            password=config.password.get_secret_value()
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):

        # mqtt_client.on_message = lambda client, userdata, message: asyncio.create_task(mqtt_on_message(client, userdata, message))
        self.client.connect_async(
            host=self.config.host,
            port=self.config.port
        )

    def on_dbus_signal(self, bus_name: str, path: str, interface: str, signal: str, topic, msg: dict[str, Any]):
        payload = json.dumps(msg)
        logger.debug(f"on_dbus_signal: payload={payload}")
        self.client.publish(topic=topic, payload=payload)

    async def run(self):
        """Runs the MQTT loop in a non-blocking way with asyncio."""
        self.client.loop_start()  # Runs Paho's loop in a background thread
        await asyncio.Event().wait()  # Keeps the coroutine alive

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            logger.warning(f"on_connect: Failed to connect: {reason_code}. Will retry connection")
        else:
            logger.info(f"on_connect: Connected to {self.config.host}:{self.config.port}")
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("dbus2mqtt")


    def on_message(self, client, userdata, msg):
        logger.info(f"on_message: client={client}, userdata={userdata}, msg={msg}")
