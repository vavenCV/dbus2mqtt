# dbus2mqtt

A Python application that let you expose Linux dbus commands and signals on MQTT topics.

Features

* Dbus signal forwarding to MQTT
* MQTT payload transformation using Jinja templating
* MQTT payload enrichment with additional dbus calls

Feature TODO list

* Implement command handling from MQTT to dbus
* Add support for timer triggers. The PropertiesChanged signal is not triggered for all properties like 'Position'
* Stability testing and play around with dbus-next to see how it behaves. An alternative might be python-sdbus 

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
# TODO
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
# https://github.com/altdesktop/playerctl/blob/master/playerctl/playerctl-player-manager.c
dbus-monitor

busctl --user introspect org.freedesktop.DBus /org/freedesktop/DBus

playerctl -l
busctl --user introspect org.mpris.MediaPlayer2.vlc /org/mpris/MediaPlayer2

dbus-send --print-reply --session --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris

```
