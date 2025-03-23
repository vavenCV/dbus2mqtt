from dbus_next.aio import MessageBus, ProxyObject, ProxyInterface
from dbus_next.introspection import Interface

import asyncio

class MprisToMqtt:

    def __init__(self, bus: MessageBus):
        # self.bus = MessageBus()
        self.bus = bus
        self.proxies: dict[str, ProxyObject] = {}

    async def connect(self):

        if not self.bus.connected:
            self.proxies.clear()
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

            
    
    # async def setup(self):

    #     self.bus.introspect.

    async def connect_player(self, bus_name: str, path: str):

        introspection = await self.bus.introspect(bus_name, path)
        obj = self.bus.get_proxy_object(bus_name, path, introspection)
        
        assert self.proxies.get(bus_name) == None
        self.proxies[bus_name] = obj

        # player = obj.get_interface('org.mpris.MediaPlayer2.Player')
        properties = obj.get_interface('org.freedesktop.DBus.Properties')

        # start listening for events
        properties.on_properties_changed(self.on_properties_changed)

    async def disconnect_player(self, bus_name: str):

        obj = self.proxies.get(bus_name)

        assert obj is not None

        # stop listening for events
        properties = obj.get_interface('org.freedesktop.DBus.Properties')
        properties.off_properties_changed(self.on_properties_changed)

        del self.proxies[bus_name]

    def dbus_name_acquired_callback(self, name):
        print(f'NameAcquired: name={name}')

    def dbus_name_lost_callback(self, name):
        print(f'NameLost: name={name}')

    async def dbus_name_owner_changed_callback(self, name, old_owner, new_owner):

        # .NameAcquired                         signal    s         -                                        -
        # .NameLost                             signal    s         -                                        -
        # .NameOwnerChanged

        # for changed, variant in changed_properties.items():
        # print(f'NameOwnerChanged: name={name}, old_owner={old_owner}, new_owner={new_owner}')
        if "org.mpris.MediaPlayer2" in name:
            if new_owner and not old_owner:
                print(f'NameOwnerChanged-ADDED: name={name}')

                # await mprisToMqtt.connect_player('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2')
                await self.connect_player(name, "/org/mpris/MediaPlayer2")
            if old_owner and not new_owner:
                print(f'NameOwnerChanged-REMOVED: name={name}')
                await self.disconnect_player(name)

    def on_properties_changed(self, interface_name, changed_properties, invalidated_properties):
        for changed, variant in changed_properties.items():
            print(f'property changed: interface_name={interface_name}, {changed} - {variant.value}')


async def main():

    bus = MessageBus()
    mprisToMqtt = MprisToMqtt(bus)

    await mprisToMqtt.connect()

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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
