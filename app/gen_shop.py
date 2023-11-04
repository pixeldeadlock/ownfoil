import os
import json
import logging
from utils import read_config, update_conf_from_env, CONFIG_KEYS

logger = logging.getLogger(__name__)

def list_dirs_and_files(path, valid_extensions):
    valid_extensions_set = set(valid_extensions)
    all_files = []
    all_dirs = []

    for entry in os.scandir(path):
        if entry.is_dir():
            all_dirs.append(entry.path)
            dirs, files = list_dirs_and_files(entry.path, valid_extensions_set)
            all_dirs.extend(dirs)
            all_files.extend(files)
        else:
            _, ext = os.path.splitext(entry.path)
            if ext.lstrip('.') in valid_extensions_set:
                all_files.append(entry.path)

    return all_dirs, all_files

def get_shop_game_files(path, config):
    # Provide default valid extensions if not found in config
    valid_extensions = config.get("shop", {}).get("valid_ext", [".nsp",".xci"])

    dirs, files = list_dirs_and_files(path, valid_extensions)

    rel_dirs = [os.path.join('..', os.path.relpath(s, path)) for s in dirs]
    rel_files = [os.path.join('..', os.path.relpath(s, path)) for s in files]

    logger.info(f'Found {len(dirs)} directories, {len(files)} game/save files')

    games = [{'url': rel_path, 'size': round(os.path.getsize(game))} for game, rel_path in zip(files, rel_files)]

    return rel_dirs, games

def initialize_shop(path):
    return read_config(os.path.join(path, "shop_template.toml"))

def generate_shop(path, config):
    shop = initialize_shop(path)

    shop_dirs, shop_files = get_shop_game_files(path, config)
    shop['directories'] = shop_dirs
    shop['files'] = shop_files

    for ext in ['json', 'tfl']:
        output_file = os.path.join(path, f'shop.{ext}')
        try:
            with open(output_file, 'w') as f:
                json.dump(shop, f, indent=4)
            logger.info(f'Successfully wrote {output_file}')
        except Exception as e:
            logger.error(f'Failed to write {output_file}, error was:\n{e}')
