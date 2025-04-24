
import os

from typing import cast

import dotenv
import jsonargparse

from dbus2mqtt.config import Config
from dbus2mqtt.main import custom_yaml_load

FILE_DIR = os.path.dirname(__file__)

def test_off_string_value():

    dotenv.load_dotenv(".env.example")

    jsonargparse.set_loader("yaml_custom", custom_yaml_load)
    parser = jsonargparse.ArgumentParser(default_env=True, env_prefix=False, parser_mode="yaml_custom")
    parser.add_class_arguments(Config)

    # parser.(format="yaml")

    cfg = parser.parse_path(f"{FILE_DIR}/fixtures/payload_template_off.yaml")
    config: Config = cast(Config, parser.instantiate_classes(cfg))

    assert config is not None

    action = config.flows[0].actions[0]
    assert action.type == "mqtt_publish"
    assert action.payload_template == {
        'PlaybackStatus': 'Off',  # This is the real test, it was False before the 'yaml_custom' loader
        'TestFalseString': False  # This is one that should also be fixed. For now it's what it is
    }
