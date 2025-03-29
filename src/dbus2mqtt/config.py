import fnmatch

from dataclasses import dataclass, field
from typing import Any

import yaml

from jinja2 import (
    BaseLoader,
    Environment,
    StrictUndefined,
)
from pydantic import SecretStr

env = Environment(
    loader=BaseLoader(),
    extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'],
    # autoescape=select_autoescape()
    # trim_blocks=True,
    # lstrip_blocks=True,
    undefined=StrictUndefined,
    enable_async=True
)

@dataclass
class SignalHandlerConfig:
    signal: str
    filter: str
    payload_template: str | dict[str, Any]
    mqtt_topic: str

    async def matches_filter(self, *args) -> bool:
        res = await env.from_string(self.filter).render_async(args=args)
        return res == "True"

    async def render_payload_template(self, args, context: dict[str, Any]) -> Any:
        # print(f"a: {self.payload_template}, args={args}")
        template = self.payload_template
        dict_template = isinstance(template, dict)
        if dict_template:
            template = yaml.safe_dump(template)

        rendered = await env.from_string(template).render_async(args=args, **context)
        rendered = yaml.safe_load(rendered)

        return rendered

    async def render_mqtt_topic(self, context: dict[str, Any]) -> Any:
        rendered = await env.from_string(self.mqtt_topic).render_async(**context)
        return rendered

@dataclass
class MethodConfig:
    method: str

@dataclass
class PropertyConfig:
    property: str

@dataclass
class InterfaceConfig:
    interface: str
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


@dataclass
class SubscriptionConfig:
    bus_name: str
    path: str
    interfaces: list[InterfaceConfig] = field(default_factory=list)

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
