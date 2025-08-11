---
hide:
  - toc
---

# Linux Desktop (WIP)

## Introduction

> **Warning:** This is not working, dbus-next is validating property names and bails on `power-saver-enable`

## Setup activities

Trying out this example

```bash
uv run dbus2mqtt --config docs/examples/linux_desktop.yaml
```

## Features

* Desktop notifications

## Commands

The following table lists the supported commands, their descriptions, and an example JSON payload for invoking them via MQTT.

dbus methods can be invoked by sendig the JSON payload to MQTT topic `dbus2mqtt/Desktop/command`.

For an overview of commands have a look at <https://docs.flatpak.org/en/latest/portal-api-reference.html>

## Desktop notifications

<https://specifications.freedesktop.org/notification-spec/1.3/>
<https://specifications.freedesktop.org/icon-naming-spec/latest/>
