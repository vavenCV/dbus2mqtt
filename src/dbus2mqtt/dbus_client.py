
from dbus2mqtt.config import DbusConfig, SubscriptionConfig, InterfaceConfig

import json

import re
import dbus_next.aio as dbus_aio
import dbus_next.introspection as dbus_introspection
import dbus_next.signature as dbus_signature

import fnmatch
import logging


# from dbus_next.aio.proxy_object import ProxyObject as DbusProxyObject
# from dbus_next.introspection import Interface as DbusInterface

# class BusSubscriptionState:
#     bus_name: str

#     dbus_aio.proxy_object.ProxyObject



logger = logging.getLogger(__name__)

class DbusClient:

    def __init__(self, config: DbusConfig, bus: dbus_aio.message_bus.MessageBus):
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
            interface: dbus_introspection.Interface = proxy.introspection

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
    def get_subscription(self, bus_name: str, path: str) -> SubscriptionConfig | None:
        for subscription in self.config.subscriptions:
            if fnmatch.fnmatchcase(bus_name, subscription.bus_name) and fnmatch.fnmatchcase(path, subscription.path):
                return subscription


    @staticmethod
    def camel_to_snake(name):
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()

    async def subscribe_interface(self, bus_name: str, path: str, introspection: dbus_introspection.Node, interface: dbus_introspection.Interface, si: InterfaceConfig):
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
