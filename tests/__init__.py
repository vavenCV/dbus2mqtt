
from pydantic import SecretStr

from dbus2mqtt import AppContext, config
from dbus2mqtt.event_broker import EventBroker
from dbus2mqtt.template.templating import TemplateEngine


def mocked_app_context():

    test_config = config.Config(dbus=config.DbusConfig(
        subscriptions=[
            config.SubscriptionConfig(
                bus_name="test.bus_name.*",
                path="/",
            )
        ]
    ),
    mqtt=config.MqttConfig(
        host="localhost",
        username="test",
        password=SecretStr("test")
    ),
    flows=[]
    )

    event_broker = EventBroker()
    template_engine = TemplateEngine()
    app_context = AppContext(test_config, event_broker, template_engine)

    return app_context
