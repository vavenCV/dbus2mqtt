
import os

from typing import cast

import dotenv

from dbus2mqtt.config import Config
from dbus2mqtt.config.jsonarparse import new_argument_parser

FILE_DIR = os.path.dirname(__file__)

def test_off_string_value():

    dotenv.load_dotenv(".env.example")

    parser = new_argument_parser()
    parser.add_class_arguments(Config)

    cfg = parser.parse_path(f"{FILE_DIR}/fixtures/payload_template_off.yaml")
    config: Config = cast(Config, parser.instantiate_classes(cfg))

    assert config is not None

    action = config.flows[0].actions[0]
    assert action.type == "mqtt_publish"
    assert action.payload_template == {
        'PlaybackStatus': 'Off',  # This is the real test, it was False before the 'yaml_custom' loader
        'TestFalseString': False  # This is one that should also be fixed. For now it's what it is
    }
