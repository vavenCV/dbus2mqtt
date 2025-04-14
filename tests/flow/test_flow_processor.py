from datetime import datetime
from typing import Any

import pytest

from dbus2mqtt.config import (
    FlowActionContextSetConfig,
    FlowActionMqttPublishConfig,
    FlowConfig,
    FlowTriggerScheduleConfig,
)
from dbus2mqtt.flow.flow_processor import FlowProcessor, FlowTriggerMessage
from tests import mocked_app_context


@pytest.mark.asyncio
async def test_schedule_trigger():

    context: dict[str, Any] = {}
    trigger_config = FlowTriggerScheduleConfig()
    flow_config = FlowConfig(
        triggers=[
            trigger_config
        ],
        actions=[
            FlowActionContextSetConfig(
                context={
                    "var1": "{{ subscription_bus_name }}"
                }
            ),
            FlowActionMqttPublishConfig(
                topic="dbus2mqtt/test",
                payload_template="{{ var1 }}"
            )
        ]
    )

    app_context = mocked_app_context()
    app_context.config.dbus.subscriptions[0].flows = [flow_config]

    processor = FlowProcessor(app_context)

    await processor._process_flow_trigger(
        FlowTriggerMessage(flow_config, trigger_config, datetime.now(), context)
    )

    mqtt_message = app_context.event_broker.mqtt_publish_queue.sync_q.get_nowait()

    assert mqtt_message is not None
    assert mqtt_message.payload == "test.bus_name.*"
