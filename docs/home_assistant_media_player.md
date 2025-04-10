# Mediaplayer integration with Home Assistant

Trying it out

```bash
uv run dbus2mqtt --config docs/home_assistant_media_player.yaml
```

This example shows how this dbus2mqtt can act as a bridge between the MPRIS player and Home Assistant.

Features:
* dbus subscription using `org.mpris.MediaPlayer2.*` wildcard to support multiple concurrent MRPIS players
* Every 5 seconds, the state if the `first` known MPRIS player is published to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/state`
* Every MPRIS property update immediately publishes the state to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/state` 
* Suppport for player commands (see table below)

# Player Commands

The following table lists the supported player commands, their descriptions, and an example JSON payload for invoking them via MQTT.

dbus methods can be invoked by sendig the JSON payload to MQTT topic `dbus2mqtt/org.mpris.MediaPlayer2/command`. Method calls will be done for all matching players

| Interface                       | Method     | Description                              | Example JSON Payload                                                               |
|---------------------------------|------------|------------------------------------------|------------------------------------------------------------------------------------|
| `org.mpris.MediaPlayer2.Player` | `Pause`    | Pauses playback                          | `{ "method": "Pause" }`                                                            |
| `org.mpris.MediaPlayer2.Player` | `Play`     | Starts playback                          | `{ "method": "Play" }`                                                             |
| `org.mpris.MediaPlayer2.Player` | `PlayPause`| Toggles between play and pause           | `{ "method": "PlayPause" }`                                                        |
| `org.mpris.MediaPlayer2.Player` | `OpenUri`  | Opens a media file or stream by URI      | `{ "method": "OpenUri", "args": ["<URI>"] }`                                       |
| `org.mpris.MediaPlayer2.Player` | `Stop`     | Stops playback                           | `{ "method": "Stop" }`                                                             |
| `org.mpris.MediaPlayer2`        | `Quit`     | Quits the media player                   | `{ "method": "Quit" }`                                                             |

Replace `<URI>` in the `OpenUri` payload with the desired media URI.

For an overview of MPRIS commands have a look at <https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html>

# Home Assistant configuration

Example HASS configuration is based upon <https://github.com/TroyFernandes/hass-mqtt-mediaplayer>

First step is te create a MQTT sensor for the topic `dbus2mqtt/org.mpris.MediaPlayer2/state`

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
        {% else %}
          idle
        {% endif %}

media_player:  
  - platform: mqtt-mediaplayer
    name: "MPRIS Media Player"
    topic:
      song_title: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:title'] }}"
      song_artist: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:artist'] | first }}"
      song_album: "{{ state_attr('sensor.mpris_media_player', 'Metadata')['xesam:album'] }}"
      song_volume: "{{ state_attr('sensor.mpris_media_player', 'Volume') }}"
      player_status: "{{ states('sensor.mpris_media_player') }}"
      volume:
        service: mqtt.publish
        data:
          topic: dbus2mqtt/org.mpris.MediaPlayer2/command
          payload: '{"command": "set_property", "property": "Volume", "value": {{volume}} }'
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
    turn_off:
      service: mqtt.publish
      data:
        topic: dbus2mqtt/org.mpris.MediaPlayer2/command
        payload: '{"method": "Quit"}'
```

# Other solutions

Another MQTT Mediaplayer plugin for HASS is <https://github.com/jonaseickhoff/hass-multiroom-mqtt-mediaplayer> 
