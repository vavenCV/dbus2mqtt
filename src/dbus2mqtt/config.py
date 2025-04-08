import fnmatch

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import SecretStr

from dbus2mqtt.template.templating import TemplateEngine


@dataclass
class SignalHandlerConfig:
    signal: str
    filter: str
    payload_template: str | dict[str, Any]
    mqtt_topic: str

    def matches_filter(self, template_engine: TemplateEngine, *args) -> bool:
        res = template_engine.render_template(self.filter, { "args": args })
        return res == "True"

    async def render_payload_template(self, template_engine: TemplateEngine, context: dict[str, Any]) -> Any:
        return await template_engine.async_render_template(self.payload_template, context)

    def render_mqtt_topic(self, template_engine: TemplateEngine, context: dict[str, Any]) -> Any:
        return template_engine.render_template(self.mqtt_topic, context)

@dataclass
class MethodConfig:
    method: str

@dataclass
class PropertyConfig:
    property: str

@dataclass
class InterfaceConfig:
    interface: str
    mqtt_call_method_topic: str | None
    signal_handlers: list[SignalHandlerConfig] = field(default_factory=list)
    methods: list[MethodConfig] = field(default_factory=list)
    properties: list[PropertyConfig] = field(default_factory=list)

    def signal_handlers_by_signal(self) -> dict[str, list[SignalHandlerConfig]]:
        res: dict[str, list[SignalHandlerConfig]] = {}

        for handler in self.signal_handlers:
            if handler.signal not in res:
                res[handler.signal] = []
            res[handler.signal].append(handler)

        return res

    def render_mqtt_call_method_topic(self, template_engine: TemplateEngine, context: dict[str, Any]) -> Any:
        return template_engine.render_template(self.mqtt_call_method_topic, context)

@dataclass
class FlowTriggerMqttConfig:
    type: Literal["mqtt"]
    topic: str
    filter: str | None = None

@dataclass
class FlowTriggerScheduleConfig:
    type: Literal["schedule"]
    cron: dict[str, Any] | None = None
    interval: dict[str, Any] | None = None

@dataclass
class FlowTriggerDbusSignalConfig:
    type: Literal["dbus_signal"]
    bus_name: str
    path: str
    interface: str
    signal: str

FlowTriggerConfig = FlowTriggerMqttConfig | FlowTriggerScheduleConfig | FlowTriggerDbusSignalConfig

@dataclass
class FlowActionContextSet:
    type: Literal["context_set"]
    context: dict[str, Any] | None = None
    global_context: dict[str, Any] | None = None

@dataclass
class FlowActionMqttPublish:
    type: Literal["mqtt_publish"]
    topic: str
    payload_template: str | dict[str, Any]
    payload_type: Literal["json", "yaml", "text"] = "json"

FlowActionConfig = FlowActionMqttPublish | FlowActionContextSet

@dataclass
class FlowConfig:
    name: str
    triggers: list[FlowTriggerConfig]
    actions: list[FlowActionConfig]

@dataclass
class SubscriptionConfig:
    bus_name: str
    path: str
    interfaces: list[InterfaceConfig] = field(default_factory=list)
    flows: list[FlowConfig] = field(default_factory=list)

@dataclass
class DbusConfig:
    subscriptions: list[SubscriptionConfig]

    def is_bus_name_configured(self, bus_name: str) -> bool:

        for subscription in self.subscriptions:
            if fnmatch.fnmatchcase(bus_name, subscription.bus_name):
                return True
        return False

    def get_subscription_configs(self, bus_name: str, path: str) -> list[SubscriptionConfig]:
        res: list[SubscriptionConfig] = []
        for subscription in self.subscriptions:
            if fnmatch.fnmatchcase(bus_name, subscription.bus_name) and fnmatch.fnmatchcase(path, subscription.path):
                res.append(subscription)
        return res

@dataclass
class MqttConfig:
    host: str
    username: str
    password: SecretStr
    port: int = 1883

@dataclass
class Config:
    mqtt: MqttConfig
    dbus: DbusConfig
    flows: list[FlowConfig] = field(default_factory=list)
