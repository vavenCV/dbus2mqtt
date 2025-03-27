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
    undefined=StrictUndefined
)

@dataclass
class SignalConfig:
    signal: str
    filter: str
    payload_template: str | dict[str, Any]

    def matches_filter(self, *args) -> bool:
        res = env.from_string(self.filter).render(args=args)
        return res == "True"

    def render_payload_template(self, *args) -> Any:
        # print(f"a: {self.payload_template}, args={args}")
        template = self.payload_template
        dict_template = isinstance(template, dict)
        if dict_template:
            template = yaml.safe_dump(template)

        rendered = env.from_string(template).render(args=args)
        rendered = yaml.safe_load(rendered)

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
    signals: list[SignalConfig] = field(default_factory=list)
    methods: list[MethodConfig] = field(default_factory=list)
    properties: list[PropertyConfig] = field(default_factory=list)

@dataclass
class SubscriptionConfig:
    bus_name: str
    path: str
    interfaces: list[InterfaceConfig] = field(default_factory=list)

@dataclass
class DbusConfig:
    subscriptions: list[SubscriptionConfig]

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
