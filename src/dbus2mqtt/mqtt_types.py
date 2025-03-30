
from collections.abc import Callable
from typing import Any


class MqttMsgHandler:

    handler: Callable[[str, dict[str, Any]], None]

    def on_mqtt_msg(self, topic: str, payload: dict[str, Any]):
        if self.handler:
            self.handler(topic, payload)
