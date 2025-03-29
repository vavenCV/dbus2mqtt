# dbus2mqtt

Running from source can be done using `uv`

```bash
uv run main.py --config config.yaml
```

## mqtt commands

Below a list of mqtt command examples

topic: "musicbee/command"
payload

```json
{
    "command":"volume_set",
    "args":{
        "volume":10
    }
}
```

## dbus debugging

```bash
uv run dbus2mqtt

# https://dbus.freedesktop.org/doc/dbus-tutorial.html
# https://dbus.freedesktop.org/doc/dbus-specification.html
# https://github.com/altdesktop/playerctl/blob/master/playerctl/playerctl-player-manager.c
dbus-monitor

busctl --user introspect org.freedesktop.DBus /org/freedesktop/DBus

playerctl -l
busctl --user introspect org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2

dbus-send --print-reply --session --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris

```

## alternative dbus libraries

<https://github.com/python-sdbus/python-sdbus>
