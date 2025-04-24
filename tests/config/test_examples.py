
import os

import dotenv
import jsonargparse

from dbus2mqtt.config import Config
from dbus2mqtt.main import custom_yaml_load

FILE_DIR = os.path.dirname(__file__)

def test_home_assistant_media_player_example():

    dotenv.load_dotenv(".env.example")

    jsonargparse.set_loader("yaml_custom", custom_yaml_load)
    parser = jsonargparse.ArgumentParser(default_env=True, env_prefix=False, parser_mode="yaml_custom")
    parser.add_class_arguments(Config)

    cfg = parser.parse_path(f"{FILE_DIR}/../../docs/examples/home_assistant_media_player.yaml")
    config = parser.instantiate_classes(cfg)

    assert config is not None

def test_linux_desktop_example():
    dotenv.load_dotenv(".env.example")

    jsonargparse.set_loader("yaml_custom", custom_yaml_load)
    parser = jsonargparse.ArgumentParser(default_env=True, env_prefix=False, parser_mode="yaml_custom")
    parser.add_class_arguments(Config)

    cfg = parser.parse_path(f"{FILE_DIR}/../../docs/examples/linux_desktop.yaml")
    config = parser.instantiate_classes(cfg)

    assert config is not None
