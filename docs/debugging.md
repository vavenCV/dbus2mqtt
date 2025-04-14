# Debugging

## Running from source

```bash
uv run main.py --config config.yaml
```

## dbus debugging

```bash
uv run dbus2mqtt

# https://dbus.freedesktop.org/doc/dbus-tutorial.html
# https://dbus.freedesktop.org/doc/dbus-specification.html
dbus-monitor

busctl --user introspect org.freedesktop.DBus /org/freedesktop/DBus

playerctl -l
busctl --user introspect org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2

dbus-send --print-reply --session --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris
```
