import os
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import logging

# Set up logging for the module
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s %(name)s: %(message)s', level=logging.INFO)

# Set environment variables to override properties from configuration file
CONFIG_KEYS = {
    "ROOT_DIR": "root_dir",
    "SCAN_INTERVAL": "shop.scan_interval",
    "SHOP_TEMPLATE": "shop.template",
    "SAVE_ENABLED": "saves.enabled",
    "SAVE_INTERVAL": "saves.interval"
}

def update_conf_from_env(keys_map, config):
    for env, toml_path in keys_map.items():
        if env in os.environ:
            current_dict = config
            keys = toml_path.split(".")
            for key in keys[:-1]:
                current_dict = current_dict[key]
            current_dict[keys[-1]] = os.environ[env]

def read_config(toml_file):
    try:
        with open(toml_file, mode="rb") as fp:
            config = tomllib.load(fp)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file {toml_file} not found.")
        raise FileNotFoundError(f"Configuration file {toml_file} not found.")
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        raise