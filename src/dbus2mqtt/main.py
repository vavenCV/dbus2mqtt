import asyncio
import logging
import signal
import sys

from typing import cast

import dbus_next.aio as dbus_aio
import jsonargparse

from dotenv import load_dotenv

from dbus2mqtt.config import Config, DbusConfig, MqttConfig
from dbus2mqtt.dbus_client import DbusClient
from dbus2mqtt.event_broker import EventBroker
from dbus2mqtt.mqtt_client import MqttClient

logger = logging.getLogger(__name__)


async def dbus_processor_task(config: DbusConfig, event_broker: EventBroker):

    bus = dbus_aio.message_bus.MessageBus()

    dbus_client = DbusClient(config, bus, event_broker)
    await dbus_client.connect()

    loop = asyncio.get_running_loop()
    dbus_client_run_future = loop.create_future()

    await asyncio.gather(
        dbus_client_run_future,
        asyncio.create_task(dbus_client.dbus_signal_queue_processor_task()),
        asyncio.create_task(dbus_client.mqtt_receive_queue_processor_task()),
    )

async def mqtt_processor_task(config: MqttConfig, event_broker: EventBroker):

    mqtt_client = MqttClient(config, event_broker)
    mqtt_client.connect()
    mqtt_client.client.loop_start()

    loop = asyncio.get_running_loop()
    mqtt_client_run_future = loop.create_future()

    try:
        await asyncio.gather(
            mqtt_client_run_future,
            asyncio.create_task(mqtt_client.mqtt_publish_queue_processor_task()),
        )
    except asyncio.CancelledError:
        mqtt_client.client.loop_stop()

async def run(config: Config):

    event_broker = EventBroker()

    try:
        await asyncio.gather(
            dbus_processor_task(config.dbus, event_broker),
            mqtt_processor_task(config.mqtt, event_broker)
        )
    except asyncio.CancelledError:
        pass


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

    # Handle Ctrl+C gracefully
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))

    try:
        loop.run_until_complete(run(config))
    except asyncio.CancelledError:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

async def shutdown(loop):
    logger.info("Shutting down event loop...")
    tasks = asyncio.all_tasks() - {asyncio.current_task()}
    for task in tasks:
        task.cancel()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(f"Sucessfully stopped {len(results)} tasks")
    loop.stop()
