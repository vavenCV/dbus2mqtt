import asyncio
import logging
import sys

from typing import cast

import dbus_next.aio as dbus_aio
import jsonargparse

from dotenv import load_dotenv

from dbus2mqtt.config import Config, DbusConfig, MqttConfig
from dbus2mqtt.dbus_client import DbusClient
from dbus2mqtt.dbus_subscription import DbusSignalHandler
from dbus2mqtt.mqtt_client import MqttClient

logger = logging.getLogger(__name__)


async def setup_dbus(config: DbusConfig, dbus_signal_handler: DbusSignalHandler):

    bus = dbus_aio.message_bus.MessageBus()
    dbus_client = DbusClient(config, bus, dbus_signal_handler)
    await dbus_client.connect()

    loop = asyncio.get_running_loop()
    await loop.create_future()

async def setup_mqtt(config: MqttConfig, dbus_signal_handler: DbusSignalHandler):

    mqtt_client = MqttClient(config, dbus_signal_handler)
    mqtt_client.connect()

    # run mqtt client forever
    loop = asyncio.get_running_loop()
    loop.create_task(asyncio.to_thread(mqtt_client.client.loop_forever))

async def run(loop, config: Config):

    dbus_signal_handler = DbusSignalHandler()

    await asyncio.gather(
        setup_dbus(config.dbus, dbus_signal_handler),
        setup_mqtt(config.mqtt, dbus_signal_handler)
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
