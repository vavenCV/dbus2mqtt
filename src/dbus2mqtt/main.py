import asyncio
import logging
import sys

from typing import cast

import dbus_next.aio as dbus_aio
import jsonargparse

from dotenv import load_dotenv

from dbus2mqtt import AppContext
from dbus2mqtt.config import Config
from dbus2mqtt.dbus.dbus_client import DbusClient
from dbus2mqtt.event_broker import EventBroker
from dbus2mqtt.flow.flow_processor import FlowProcessor, FlowScheduler
from dbus2mqtt.mqtt.mqtt_client import MqttClient
from dbus2mqtt.template.dbus_template_functions import jinja_custom_dbus_functions
from dbus2mqtt.template.templating import TemplateEngine

logger = logging.getLogger(__name__)


async def dbus_processor_task(app_context: AppContext):

    bus = dbus_aio.message_bus.MessageBus()

    dbus_client = DbusClient(app_context, bus)
    app_context.templating.add_functions(jinja_custom_dbus_functions(dbus_client))

    await dbus_client.connect()

    loop = asyncio.get_running_loop()
    dbus_client_run_future = loop.create_future()

    await asyncio.gather(
        dbus_client_run_future,
        asyncio.create_task(dbus_client.dbus_signal_queue_processor_task()),
        asyncio.create_task(dbus_client.mqtt_receive_queue_processor_task())
    )

async def mqtt_processor_task(app_context: AppContext):

    mqtt_client = MqttClient(app_context)

    mqtt_client.connect()
    mqtt_client.client.loop_start()

    loop = asyncio.get_running_loop()
    mqtt_client_run_future = loop.create_future()

    try:
        await asyncio.gather(
            mqtt_client_run_future,
            asyncio.create_task(mqtt_client.mqtt_publish_queue_processor_task())
        )
    except asyncio.CancelledError:
        mqtt_client.client.loop_stop()

async def flow_processor_task(app_context: AppContext):

    flow_processor = FlowProcessor(app_context)

    await asyncio.gather(
        asyncio.create_task(flow_processor.flow_processor_task())
    )

async def flow_scheduler_task(app_context: AppContext):

    flow_scheduler = FlowScheduler(app_context)

    await asyncio.gather(
        asyncio.create_task(flow_scheduler.scheduler_task())
    )

async def run(config: Config):

    event_broker = EventBroker()
    template_engine = TemplateEngine()

    app_context = AppContext(config, event_broker, template_engine)

    try:
        await asyncio.gather(
            dbus_processor_task(app_context),
            mqtt_processor_task(app_context),
            flow_processor_task(app_context),
            flow_scheduler_task(app_context)
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
        apscheduler_logger = logging.getLogger("apscheduler")
        apscheduler_logger.setLevel(logging.WARNING)

    logger.debug(f"config: {config}")

    asyncio.run(run(config))
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)

#     # Handle Ctrl+C gracefully
#     for sig in (signal.SIGINT, signal.SIGTERM):
#         loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))

#     try:
#         loop.run_until_complete(run(config))
#     except asyncio.CancelledError:
#         pass
#     finally:
#         loop.run_until_complete(loop.shutdown_asyncgens())
#         loop.close()

# async def shutdown(loop):
#     logger.info("Shutting down event loop...")
#     tasks = asyncio.all_tasks() - {asyncio.current_task()}
#     for task in tasks:
#         task.cancel()
#     results = await asyncio.gather(*tasks, return_exceptions=True)
#     logger.info(f"Sucessfully stopped {len(results)} tasks")
#     loop.stop()
