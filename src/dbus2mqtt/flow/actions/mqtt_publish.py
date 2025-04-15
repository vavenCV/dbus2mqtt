
import logging

from jinja2.exceptions import TemplateRuntimeError

from dbus2mqtt import AppContext
from dbus2mqtt.config import FlowActionMqttPublishConfig
from dbus2mqtt.flow import FlowAction, FlowExecutionContext
from dbus2mqtt.mqtt.mqtt_client import MqttMessage

logger = logging.getLogger(__name__)

class MqttPublishAction(FlowAction):

    def __init__(self, config: FlowActionMqttPublishConfig, app_context: AppContext):
        self.config = config
        self.event_broker = app_context.event_broker
        self.templating = app_context.templating

    async def execute(self, context: FlowExecutionContext):

        render_context = context.get_aggregated_context()

        try:
            mqtt_topic = await self.templating.async_render_template(self.config.topic, str, render_context)

            payload_res_type = str if self.config.payload_type == "text" else dict
            payload = await self.templating.async_render_template(self.config.payload_template, payload_res_type, render_context)

        except TemplateRuntimeError as e:
            logger.warning(f"Error rendering jinja template, flow: '{context.name}', error: {str(e)}. render_context={render_context}", exc_info=True)
            return
        except Exception as e:
            logger.warning(f"Error rendering jinja template, flow: '{context.name}', error: {str(e)}. render_context={render_context}", exc_info=False)
            return

        logger.debug(f"public_mqtt: flow={context.name}, payload={payload}")

        await self.event_broker.publish_to_mqtt(MqttMessage(mqtt_topic, payload, payload_serialization_type=self.config.payload_type))
