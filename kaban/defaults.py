"""A few default file paths to try if user has not specified otherwise."""

from pathlib import Path


KABAN_DIR = Path.home() / '.kaban'

TOML_FILE_PATH = KABAN_DIR / 'my_kaban_tasks.toml'
YAML_FILE_PATH = KABAN_DIR / 'my_kaban_tasks.yaml'

CONFIG_FILE_PATH = KABAN_DIR / 'config.toml'

