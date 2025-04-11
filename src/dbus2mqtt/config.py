import fnmatch
import uuid

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import SecretStr

from dbus2mqtt.template.templating import TemplateEngine


@dataclass
class SignalConfig:
    signal: str
    filter: str | None = None

    def matches_filter(self, template_engine: TemplateEngine, *args) -> bool:
        res = template_engine.render_template(self.filter, str, { "args": args })
        return res == "True"

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
    signals: list[SignalConfig] = field(default_factory=list)
    methods: list[MethodConfig] = field(default_factory=list)
    properties: list[PropertyConfig] = field(default_factory=list)

    def render_mqtt_call_method_topic(self, template_engine: TemplateEngine, context: dict[str, Any]) -> Any:
        return template_engine.render_template(self.mqtt_call_method_topic, str, context)

@dataclass
class FlowTriggerMqttConfig:
    type: Literal["mqtt"]
    topic: str
    filter: str | None = None

@dataclass
class FlowTriggerScheduleConfig:
    type: Literal["schedule"]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    cron: dict[str, Any] | None = None
    interval: dict[str, Any] | None = None

@dataclass
class FlowTriggerDbusSignalConfig:
    type: Literal["dbus_signal"]
    interface: str
    signal: str
    bus_name: str | None = None
    path: str | None = None
    filter: str | None = None

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
    """should be a dict if payload_type is json/yaml
    or a string if payload_type is text"""
    payload_type: Literal["json", "yaml", "text"] = "json"

FlowActionConfig = FlowActionMqttPublish | FlowActionContextSet

@dataclass
class FlowConfig:
    name: str
    triggers: list[FlowTriggerConfig]
    actions: list[FlowActionConfig]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

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
