# dbus2mqtt

**dbus2mqtt** is a Python application that bridges **Linux D-Bus** with **MQTT**.
It lets you forward D-Bus signals and properties to MQTT topics, call D-Bus methods via MQTT messages, and shape payloads using flexible **Jinja2 templating**.

This makes it easy to integrate Linux desktop services or system signals into MQTT-based workflows - including **Home Assistant**.

## ✨ Features

* 🔗 Forward **D-Bus signals** to MQTT topics.
* 🧠 Enrich or transform **MQTT payloads** using Jinja2 templates and dynamic D-Bus calls.
* ⚡ Trigger message publishing via **signals, timers, property changes, or startup events**.
* 📡 Expose **D-Bus methods** for remote control via MQTT messages.
* 🏠 Includes example configurations for **MPRIS** and **Home Assistant Media Player** integration.

Feature TODO list

* Remove dependency between dbus signal handling and message publishing. Allow for multiple trigger types to publish payloads. Message publishing can be triggerd by timer/initial start/property change signal. Needed because the PropertiesChanged signal is not triggered for all properties like 'Position'
* Stability testing and play around with dbus-next to see how it behaves. An alternative might be python-sdbus
* Improve error handling when deleting message with 'retain' set. WARNING:dbus2mqtt.mqtt_client:on_message: Unexpected payload, expection json, topic=dbus2mqtt/org.mpris.MediaPlayer2/command, payload=, error=Expecting value: line 1 column 1 (char 0)
* when MPRIS player disconnects, allow to publish a 'Stopped playing / quit' message on mqtt
* Property set only works the first time, need to restart after which the first set will work again
* Print found bus_names at startup (or empty if no matching subscriptions)

## Getting started with dbus2mqtt

Create a `config.yaml` file which configures with dbus services to expose. Use the following as a minimal example to get started. This configuration will expose all bus properties from the `org.mpris.MediaPlayer2.Player` interface to MQTT on the `dbus2mqtt/org.mpris.MediaPlayer2/state` topic.

```yaml
dbus:
  subscriptions:
    - bus_name: org.mpris.MediaPlayer2.*
      path: /org/mpris/MediaPlayer2
      # https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html
      interfaces:
        - interface: org.freedesktop.DBus.Properties
          signal_handlers:
            - signal: PropertiesChanged
              filter: "{{ args[0] == 'org.mpris.MediaPlayer2.Player' }}"
              payload_template: |
                {{ dbus_call('org.freedesktop.DBus.Properties', 'GetAll', 'org.mpris.MediaPlayer2.Player') }}
              mqtt_topic: dbus2mqtt/org.mpris.MediaPlayer2/state
```

MQTT connection details can either be configured in that same `config.yaml` file or in a `.env`.


```bash
MQTT__HOST=localhost
MQTT__PORT=1883
MQTT__USERNAME=
MQTT__PASSWORD=
```

To run dbus2mqtt using Python

```bash
pip install dbus2mqtt
python -m dbus2mqtt --config config.yaml
```

To run dbus2mqtt using Docker

```bash
mkdir -p $HOME/.config/dbus2mqtt
cp docs/home_assistant_media_player.yaml $HOME/.config/dbus2mqtt/config.yaml
cp .env.example $HOME/.config/dbus2mqtt/.env

docker build -t jwnmulder/dbus2mqtt:latest .
docker run --detach --name dbus2mqtt \
  --volume "$HOME"/.config/dbus2mqtt:"$HOME"/.config/dbus2mqtt \
  --env DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
  --user $(id -u):$(id -g) \
  --volume /run/user:/run/user \
  --env-file "$HOME"/.config/dbus2mqtt/.env \
  --privileged \
  --restart unless-stopped \
  jwnmulder/dbus2mqtt \
  --config "$HOME"/.config/dbus2mqtt/config.yaml

sudo docker logs dbus2mqtt -f
```

## Examples

Also see ./docs/

## Configuration reference by example

### dbus interface methods

```yaml
dbus:
  subscriptions:
    - bus_name: org.mpris.MediaPlayer2.*
      path: /org/mpris/MediaPlayer2
      interfaces:
        - interface: org.mpris.MediaPlayer2.Player
          methods:
            - method: Pause
            - method: Play
            - method: PlayPause
            - method: OpenUri
            - method: Stop
```

This configuration will expose 4 methods. Triggering methods can be done by publishing json messages to the corresponding topics.

The exact arguments to be provided depends on the dbus interface being exposed. For MPRIS these can be found here: <https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html>

topic: "dbus2mqtt/org.mpris.MediaPlayer2/?/command"

```json
{
    "method" : "PlayPause",
}
```

```json
{
    "method" : "OpenUri",
    "args":{
        "0": "..."
    }
}
```

### Jinja templating

## Running from source

Running from source can be done using `uv`

```bash
uv run main.py --config config.yaml
```

### dbus debugging

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
