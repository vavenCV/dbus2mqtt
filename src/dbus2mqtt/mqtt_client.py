
from dbus2mqtt.config import MqttConfig

import paho.mqtt.client as mqtt

import logging
import asyncio



logger = logging.getLogger(__name__)

class MqttClient:

    def __init__(self, config: MqttConfig):
        self.config = config
        self.client = mqtt.Client()

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

    async def run(self):
        """Runs the MQTT loop in a non-blocking way with asyncio."""
        self.client.loop_start()  # Runs Paho's loop in a background thread
        await asyncio.Event().wait()  # Keeps the coroutine alive
    
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, reason_code):
        logger.info(f"on_connect: reason_code={reason_code}")

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("dbus2mqtt")

    def on_message(self, client, userdata, msg):
        logger.info(f"on_message: client={client}, userdata={userdata}, msg={msg}")
