# Mediaplayer integration with Home Assistant

Trying out this example

```bash
dbus2mqtt --config docs/home_assistant_media_player.yaml
```

This example shows how this dbus2mqtt can act as a bridge between the MPRIS player and Home Assistant.

Features:

* dbus subscription using `org.mpris.MediaPlayer2.*` wildcard to support multiple concurrent MRPIS players
* Every 5 seconds, the state if the `first` known MPRIS player is published to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/state`
* Every MPRIS property update immediately publishes the state to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/state`
* Support for player commands (see below)

## Tested configurations

The following setup is known to work with Home Assistant.

| Application  | Play<br />Pause<br /> | Next<br />Previous | Seek | Volume | Stop | Quit | Media Image |
|--------------|-----------------------|--------------------|------|--------|------|------|-------------|
| `Firefox`    | ✅ | | | | | ✅ | | Youtube only |
| `VLC` | | | | | | | | |

## Player commands

The following table lists the supported player commands, their descriptions, and an example JSON payload for invoking them via MQTT.

dbus methods can be invoked by sendig the JSON payload to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/command`. Method calls will be done for all matching players

| Interface                       | Method<br />Property | Description                              | Example JSON Payload                           |
|---------------------------------|------------|------------------------------------------|------------------------------------------------|
| `org.mpris.MediaPlayer2.Player` | `Play`     | Starts playback                          | `{ "method": "Play" }`                         |
| `org.mpris.MediaPlayer2.Player` | `Pause`    | Pauses playback                          | `{ "method": "Pause" }`                        |
| `org.mpris.MediaPlayer2.Player` | `PlayPause`| Toggles between play and pause           | `{ "method": "PlayPause" }`                    |
| `org.mpris.MediaPlayer2.Player` | `Next`     | Next                                     | `{ "method": "Next" }`                         |
| `org.mpris.MediaPlayer2.Player` | `Previous` | Previous                                 | `{ "method": "Previous" }`                         |
| `org.mpris.MediaPlayer2.Player` | `Stop`     | Stops playback                           | `{ "method": "Stop" }`                         |
| `org.mpris.MediaPlayer2.Player` | `Seek`     | Seek forward or backward                | `{ "method": "Seek", "args": [60000000] }`                         |
| `org.mpris.MediaPlayer2.Player` | `Volume`   | Set volume                               | `{ "property": "Volume", "value": 50 }`                         |
| `org.mpris.MediaPlayer2`        | `Quit`     | Quits the media player                   | `{ "method": "Quit" }`                         |

For an overview of MPRIS commands have a look at <https://mpris2.readthedocs.io/en/latest/interfaces.html#mpris2.MediaPlayer2>

## Home Assistant configuration

The Home Assistant configuration below is based on the [media_player.template](https://github.com/Sennevds/media_player.template/tree/master) plugin and a working MQTT setup

Create the MQTT sensor for topic `dbus2mqtt/org.mpris.MediaPlayer2/state` and the Media Player as shown below

```yaml
mqtt:
  sensor:
    - name: "MPRIS Media Player"
      state_topic: dbus2mqtt/org.mpris.MediaPlayer2/state
      json_attributes_topic: dbus2mqtt/org.mpris.MediaPlayer2/state
      value_template: >-
        {% set status = value_json.PlaybackStatus %}
        {% if status == 'Playing' %}
          playing
        {% elif status == 'Paused' %}
          paused
        {% elif status == 'Stopped' %}
          idle
        {% else %}
          off
        {% endif %}

media_player:
  - platform: media_player_template
    media_players:
      mpris_media_player:
        # device_class: receiver
        friendly_name: MPRIS Media Player
        value_template: "{{ states('sensor.mpris_media_player') }}"

        current_volume_template: "{{ state_attr('sensor.mpris_media_player', 'Volume') }}"
        current_is_muted_template: "{{ state_attr('sensor.mpris_media_player', 'Volume') == 0 }}"
        current_position_template: "{{ state_attr('sensor.mpris_media_player', 'Position') }}"
        title_template: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:title'] }}"

        media_content_type_template: music  # needed to show 'artist'
        media_duration_template: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['mpris:length'] }}"
        album_template: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:album'] }}"
        artist_template: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:artist'] | first }}"

        # mpris:artUrl is referencing a local file when firefox is used, for now this will provide Youtube img support
        media_image_url_template: >-
          {{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:url']
            | regex_replace(
                find='https:\/\/www\\.youtube\\.com\/watch\\?v=(.*)',
                replace='https://img.youtube.com/vi/\\1/maxresdefault.jpg'
              )
          }}

        turn_off:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Quit"}'
        play:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Play"}'
        pause:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Pause"}'
        stop:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Stop"}'
        next:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Next"}'
        previous:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Previous"}'
        seek:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"method": "Seek", "args": [{{ position | int }}] }'
        set_volume:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"property": "Volume", "value": {{volume}} }'
        volume_up:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"property": "Volume", "value": 0.0 }'
        volume_down:
          service: mqtt.publish
          data:
            topic: dbus2mqtt/org.mpris.MediaPlayer2/command
            payload: '{"property": "Volume", "value": 0.0 }'
```
