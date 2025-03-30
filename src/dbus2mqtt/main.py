import asyncio
import logging
import sys

from typing import cast

import dbus_next.aio as dbus_aio
import jsonargparse

from dotenv import load_dotenv

from dbus2mqtt.config import Config, DbusConfig, MqttConfig
from dbus2mqtt.dbus_client import DbusClient
from dbus2mqtt.dbus_types import DbusSignalHandler
from dbus2mqtt.mqtt_client import MqttClient
from dbus2mqtt.mqtt_types import MqttMsgHandler

logger = logging.getLogger(__name__)


async def setup_dbus(config: DbusConfig, dbus_signal_handler: DbusSignalHandler, mqtt_msg_handler: MqttMsgHandler):

    bus = dbus_aio.message_bus.MessageBus()

    loop = asyncio.get_running_loop()

    dbus_client = DbusClient(config, bus, dbus_signal_handler, loop)
    mqtt_msg_handler.handler = dbus_client.on_mqtt_msg

    await dbus_client.connect()

    await loop.create_future()

async def setup_mqtt(config: MqttConfig, dbus_signal_handler: DbusSignalHandler, mqtt_msg_handler: MqttMsgHandler):

    mqtt_client = MqttClient(config, mqtt_msg_handler)
    dbus_signal_handler.handler = mqtt_client.on_dbus_signal

    mqtt_client.connect()

    # run mqtt client forever
    loop = asyncio.get_running_loop()
    loop.create_task(asyncio.to_thread(mqtt_client.client.loop_forever))
    # loop.run_in_executor(None, mqtt_client.client.loop_forever)

async def run(loop, config: Config):

    # handler that mbus_client uses to forward signals to mqtt_client
    dbus_signal_handler = DbusSignalHandler()

    # handler that mqtt_client uses to forward messages to dbus_client
    mqtt_msg_handler = MqttMsgHandler()

    await asyncio.gather(
        setup_dbus(config.dbus, dbus_signal_handler, mqtt_msg_handler),
        setup_mqtt(config.mqtt, dbus_signal_handler, mqtt_msg_handler)
    )


def main():

    # load environment from .env if it exists
    load_dotenv()

    # unless specified otherwise, load config from config.yaml
    parser = jsonargparse.ArgumentParser(default_config_files=["config.yaml"], default_env=True, env_prefix=False)

    parser.add_argument("--verbose", "-v", nargs="?", const=True, help="Enable verbose logging")
    parser.add_argument("--config", action="config")
    parser.add_class_arguments(Config)

    cfg = parser.parse_args()

    config: Config = cast(Config, parser.instantiate_classes(cfg))

    if cfg.verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logger.debug(f"config: {config}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(loop, config))
