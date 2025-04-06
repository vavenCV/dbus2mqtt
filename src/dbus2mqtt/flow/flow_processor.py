import asyncio
import logging

from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dbus2mqtt import AppContext
from dbus2mqtt.actions.context_set import ContextSetAction
from dbus2mqtt.actions.mqtt_publish import MqttPublishAction
from dbus2mqtt.config import FlowTriggerConfig
from dbus2mqtt.event_broker import FlowTriggerMessage
from dbus2mqtt.flow import FlowAction, FlowExecutionContext

logger = logging.getLogger(__name__)

class FlowScheduler:

    def __init__(self, app_context: AppContext):
        self.config = app_context.config
        self.event_broker = app_context.event_broker

    async def flow_strigger(self, flow, trigger_config: FlowTriggerConfig):
        trigger = FlowTriggerMessage(flow, trigger_config, datetime.now())
        await self.event_broker.flow_trigger_queue.async_q.put(trigger)

    async def scheduler_task(self):

        scheduler = AsyncIOScheduler()

        for flow in self.config.flows:
            for trigger in flow.triggers:
                if trigger.type == "schedule":
                    if trigger.interval:
                        # Each schedule gets its own job
                        scheduler.add_job(self.flow_strigger, "interval", args=[flow, trigger], **trigger.interval)
                    elif trigger.cron:
                        # Each schedule gets its own job
                        scheduler.add_job(self.flow_strigger, "cron", args=[flow, trigger], **trigger.cron)

        scheduler.start()
        while True:
            await asyncio.sleep(1000)

class FlowProcessor:

    def __init__(self, app_context: AppContext):
        self.app_context = app_context
        self.config = app_context.config
        self.event_broker = app_context.event_broker

        self._global_flow_context: dict[str, Any] = {}
        self._flow_actions = self._setup_flow_actions()

    def _setup_flow_actions(self) -> dict[str, list[FlowAction]]:
        res: dict[str, list[FlowAction]] = {}
        for flow_config in self.config.flows:
            res[flow_config.name] = []
            for action_config in flow_config.actions:
                action = None
                if action_config.type == "context_set":
                    action = ContextSetAction(action_config, self.app_context)
                if action_config.type == "mqtt_publish":
                    action = MqttPublishAction(action_config, self.app_context)
                if action:
                    res[flow_config.name].append(action)

        return res

    async def flow_processor_task(self):
        """Continuously processes messages from the async queue."""

        logger.info(f"flow_processor_task: configuring flows={[f.name for f in self.config.flows]}")

        while True:
            flow_trigger_message = await self.event_broker.flow_trigger_queue.async_q.get()  # Wait for a message
            try:
                logger.info(f"on_trigger: {flow_trigger_message.flow_trigger_config.type}, time={flow_trigger_message.timestamp.isoformat()}")

                flow_name = flow_trigger_message.flow_config.name
                context = FlowExecutionContext(name="global", global_flow_context=self._global_flow_context)

                flow_actions = self._flow_actions[flow_name]
                for action in flow_actions:
                    await action.execute(context)

            except Exception as e:
                logger.warning(f"dbus_signal_queue_processor_task: Exception {e}", exc_info=True)
            finally:
                self.event_broker.flow_trigger_queue.async_q.task_done()

# # Create a flow from the YAML configuration
# for flow_config in config['flows']:
#     flow_name = flow_config['name']
#     triggers = flow_config.get('triggers', [])
#     actions = flow_config.get('actions', [])

#     with Flow(flow_name) as flow:
#         data = "sensor_data"
#         for action in actions:
#             if action['type'] == 'python_script':
#                 process_data(data)
#             elif action['type'] == 'mqtt_publish':
#                 mqtt_publish(action['topic'], action['message_template'], data)

#         # Add scheduling trigger if defined
#         for trigger in triggers:
#             if trigger['type'] == 'schedule' and 'cron' in trigger:
#                 flow.schedule = CronSchedule(cron=trigger['cron'])
