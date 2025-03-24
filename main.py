import asyncio
import logging

from dataclasses import dataclass, field
from typing import cast
import json

import re
import dbus_next.aio as dbus_aio
import dbus_next.introspection as dbus_introspection
import dbus_next.signature as dbus_signature

import fnmatch
import jsonargparse

# from dbus_next.aio.proxy_object import ProxyObject as DbusProxyObject
# from dbus_next.introspection import Interface as DbusInterface

@dataclass
class Signal:
    signal: str

@dataclass
class Method:
    method: str

@dataclass
class Property:
    property: str

@dataclass
class Interface:
    interface: str
    signals: list[Signal] = field(default_factory=list)
    methods: list[Method] = field(default_factory=list)
    properties: list[Property] = field(default_factory=list)

@dataclass
class Subscription:
    bus_name: str
    path: str
    interfaces: list[Interface] = field(default_factory=list)

@dataclass
class Config:
    subscriptions: list[Subscription]

# class BusSubscriptionState:
#     bus_name: str

#     dbus_aio.proxy_object.ProxyObject


logger = logging.getLogger(__name__)

class MprisToMqtt:

    def __init__(self, config: Config, bus: dbus_aio.message_bus.MessageBus):
        self.config = config
        self.bus = bus
        # self.proxies: dict[str, BusSubscriptionState] = {}

    async def connect(self):

        if not self.bus.connected:
            # self.proxies.clear()
            await self.bus.connect()

            print(f"bus: connected={self.bus.connected}")


            introspection = await self.bus.introspect('org.freedesktop.DBus', '/org/freedesktop/DBus')
            obj = self.bus.get_proxy_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspection)
            # player = obj.get_interface('org.mpris.MediaPlayer2.Player')
            properties = obj.get_interface('org.freedesktop.DBus')

            proxy = obj.get_interface('org.freedesktop.DBus')
            interface: Interface = proxy.introspection

            print([m.name for m in interface.methods])
            print([s.name for s in interface.signals])
            # print)

            # for signal in interface.signals:
            properties.on_name_owner_changed(self.dbus_name_owner_changed_callback)
            properties.on_name_acquired(self.dbus_name_acquired_callback)
            properties.on_name_lost(self.dbus_name_lost_callback)

    def is_bus_name_configured(self, bus_name: str) -> bool:

        for subscription in self.config.subscriptions:
            if fnmatch.fnmatchcase(bus_name, subscription.bus_name):
                return True
        
        return False
    
    # async def setup(self):

    #     self.bus.introspect.
    def get_subscription(self, bus_name: str, path: str) -> Subscription | None:
        for subscription in self.config.subscriptions:
            if fnmatch.fnmatchcase(bus_name, subscription.bus_name) and fnmatch.fnmatchcase(path, subscription.path):
                return subscription


    @staticmethod
    def camel_to_snake(name):
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()

    async def subscribe_interface(self, bus_name: str, path: str, introspection: dbus_introspection.Node, interface: dbus_introspection.Interface, si: Interface):
        obj = self.bus.get_proxy_object(bus_name, path, introspection)
        obj_interface = obj.get_interface(interface.name)

        # start listening for events

        logger.debug(f"subscribe: bus_name={bus_name}, path={path}, interface={interface.name}")
        signal_names = [s.name for s in interface.signals]
        logger.debug(f"  signals: {signal_names}")

        signal_name = "PropertiesChanged"
        for signal in si.signals:
            if signal.signal in signal_names:
                logger.info(f"subscribed signal: bus_name={bus_name}, path={path}, interface={interface.name}, signal={signal.signal}")  
                signal_method_name = "on_" + self.camel_to_snake(signal.signal)
                # obj_interface[signal_method_name](self.on_signal_3)
                obj_interface.on_properties_changed(self.on_signal_3)

    async def process_interface(self, bus_name: str, path: str, introspection: dbus_introspection.Node, interface: dbus_introspection.Interface):

        # logger.debug(f"process_interface: {bus_name}, {path}, {interface}")
        subscription = self.get_subscription(bus_name, path)
        if subscription:
            logger.debug(f"subscription: {subscription.bus_name}, {subscription.path}")
            for subscription_interface in subscription.interfaces:
                if subscription_interface.interface == interface.name:
                    logger.debug(f"matching config found for bus_name={bus_name}, path={path}, interface={interface.name}")
                    await self.subscribe_interface(bus_name, path, introspection, interface, subscription_interface)

    async def visit_bus_name_path(self, bus_name: str, path: str):

        introspection = await self.bus.introspect(bus_name, path)

        if len(introspection.nodes) == 0:
            logger.info(f"leaf node: bus_name={bus_name}, path={path}, is_root={introspection.is_root}, interfaces={[i.name for i in introspection.interfaces]}")

        for interface in introspection.interfaces:
            await self.process_interface(bus_name, path, introspection, interface)

        for node in introspection.nodes:
            path_seperator = "" if path.endswith('/') else "/"
            await self.visit_bus_name_path(bus_name, f"{path}{path_seperator}{node.name}")

    async def handle_bus_name_added(self, bus_name: str):

        if not self.is_bus_name_configured(bus_name):
            return
    
        await self.visit_bus_name_path(bus_name, "/")

    async def handle_bus_name_removed(self, bus_name: str):

        pass
        # obj = self.proxies.get(bus_name)

        # if obj:
        #     # stop listening for events
        #     properties = obj.get_interface('org.freedesktop.DBus.Properties')
        #     properties.off_properties_changed(self.on_properties_changed)

        #     del self.proxies[bus_name]

    def dbus_name_acquired_callback(self, name):
        print(f'NameAcquired: name={name}')

    def dbus_name_lost_callback(self, name):
        print(f'NameLost: name={name}')

    async def dbus_name_owner_changed_callback(self, name, old_owner, new_owner):

        logger.debug(f'NameOwnerChanged: name=q{name}, old_owner={old_owner}, new_owner={new_owner}')

        if new_owner and not old_owner:
            logger.debug(f'NameOwnerChanged-ADDED: name={name}')
            await self.handle_bus_name_added(name)
        if old_owner and not new_owner:
            logger.debug(f'NameOwnerChanged-REMOVED: name={name}')
            await self.handle_bus_name_removed(name)

    def _unwrap(self, obj):
        if isinstance(obj, dbus_signature.Variant):
            logger.warn("XXXXXX")
            return obj.value
        return obj

    @staticmethod
    def variant_serializer(obj):
        if isinstance(obj, dbus_signature.Variant):
            return obj.value
        return obj

    def on_signal(self, *args):
        res = json.dumps(args, default=self.variant_serializer, indent=2)
        logger.info(f"on_signal: {res}")

    def on_signal_1(self, arg1):
        self.on_signal(arg1)

    def on_signal_2(self, arg1, arg2):
        self.on_signal(arg1, arg2)

    def on_signal_3(self, arg1, arg2, arg3):
        self.on_signal(arg1, arg2, arg3)

    def on_signal_4(self, arg1, arg2, arg3, arg4):
        self.on_signal(arg1, arg2, arg3, arg4)

    def on_signal_5(self, arg1, arg2, arg3, arg4, arg5):
        self.on_signal(arg1, arg2, arg3, arg4, arg5)

async def main(config: Config):

    bus = dbus_aio.message_bus.MessageBus()
    mpris_to_mqtt = MprisToMqtt(config, bus)

    await mpris_to_mqtt.connect()

    # introspection = await bus.introspect('org.freedesktop.DBus', '/org/freedesktop/DBus')

    # obj = bus.get_proxy_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspection)
    # # player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    # properties = obj.get_interface('org.freedesktop.DBus.Properties')

    # await mprisToMqtt.connect_player('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2')

    # obj = bus.get_proxy_object('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2', introspection)
    # print(f"obj: bus_name={obj.bus_name}, path={obj.path}, {[d.name for d in obj.introspection.interfaces]}")
    # player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    # properties = obj.get_interface('org.freedesktop.DBus.Properties')

    # # call methods on the interface (this causes the media player to play)
    # await player.call_play()

    # volume = await player.get_volume()
    # print(f'current volume: {volume}, setting to 0.5')

    # await player.set_volume(0.5)

    # listen to signals
    # def on_properties_changed(interface_name, changed_properties, invalidated_properties):
    #     for changed, variant in changed_properties.items():
    #         print(f'property changed: {changed} - {variant.value}')

    # properties.on_properties_changed(on_properties_changed)

    await loop.create_future()

if __name__ == "__main__":

    parser = jsonargparse.ArgumentParser(default_config_files=["config.yaml"])

    parser.add_argument("--verbose", "-v", nargs="?", const=True, help="Enable verbose logging")
    parser.add_class_arguments(Config)

    cfg = parser.parse_args()

    config: Config = cast(Config, parser.instantiate_classes(cfg))

    logging.basicConfig(level=logging.INFO)
    if cfg.verbose:
        logger.setLevel(level=logging.DEBUG)

    logger.debug(f"config: {config}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(config))
