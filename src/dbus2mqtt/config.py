from dataclasses import dataclass, field

from pydantic import SecretStr


@dataclass
class SignalConfig:
    signal: str

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
