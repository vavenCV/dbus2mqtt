
import logging

from dbus2mqtt import AppContext
from dbus2mqtt.config import FlowActionMqttPublish
from dbus2mqtt.flow import FlowAction, FlowExecutionContext
from dbus2mqtt.mqtt.mqtt_client import MqttMessage

logger = logging.getLogger(__name__)

class MqttPublishAction(FlowAction):

    def __init__(self, config: FlowActionMqttPublish, app_context: AppContext):
        self.config = config
        self.event_broker = app_context.event_broker
        # self.dbus_client = app_context.dbus_client
        self.templating = app_context.templating

    async def execute(self, context: FlowExecutionContext):

        # async_template_interface_context = {
        #     "dbus_call": async_dbus_call_fn
        # }

        # payload = await self.templating.render_payload_template(context={
        #     **template_interface_context, **async_template_interface_context
        # })
        render_context = context.get_aggregated_context()
        mqtt_topic = await self.templating.async_render_template(self.config.topic, render_context)
        payload = await self.templating.async_render_template(self.config.payload_template, render_context)


        logger.debug(f"public_mqtt: context={context.name}, payload={payload}")

        await self.event_broker.publish_to_mqtt(MqttMessage(mqtt_topic, payload, payload_serialization_type=self.config.payload_type))
