# Developer guide

## Specifications

Generic DBus specifications:

* [D-Bus Tutorial](https://dbus.freedesktop.org/doc/dbus-tutorial.html)
* [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html)

## Running from source

```bash
uv run main.py --config config.yaml
```

## MQTT CLI examples

```bash
source .env

mqtt() {
  uvx --from mqtt-cli mqtt \
    --host "$MQTT__HOST" \
    --user "$MQTT__USERNAME" \
    --password "$MQTT__PASSWORD" \
    "$@"
}

mqtt --help
mqtt subscribe --topic 'dbus2mqtt/#'
mqtt publish -t dbus2mqtt/Notifications/command -m '{ "method": "Notify", "args": ["App Name", 0, "icon name", "summary", "body message", [], {}, 5000] }'
```

```xml
      <arg type="s" name="app_name" direction="in"/>
      <arg type="u" name="replaces_id" direction="in"/>
      <arg type="s" name="app_icon" direction="in"/>
      <arg type="s" name="summary" direction="in"/>
      <arg type="s" name="body" direction="in"/>
      <arg type="as" name="actions" direction="in"/>
      <arg type="a{sv}" name="hints" direction="in"/>
      <arg type="i" name="expire_timeout" direction="in"/>
      <arg type="u" name="id" direction="out"/>
```

gdbus call --session \
  --dest=org.freedesktop.Notifications \
  --object-path=/org/freedesktop/Notifications \
  --method=org.freedesktop.Notifications.Notify \
  "" \
  0 \
  "icon name" \
  "summary" \
  "body message" \
  '[]' \
  '{}' \
  5000
