"""A few default file paths to try if user has not specified otherwise."""

from dataclasses import dataclass

from pathlib import Path


@dataclass
class Paths:
    kaban_dir        : Path
    toml_file_path   : Path
    yaml_file_path   : Path
    config_file_path : Path


_DEFAULT_KABAN_DIR = Path.home() / '.kaban'

DEFAULT_PATHS = Paths( _DEFAULT_KABAN_DIR
                     , _DEFAULT_KABAN_DIR / 'my_kaban_tasks.toml'
                     , _DEFAULT_KABAN_DIR / 'my_kaban_tasks.yaml'
                     , _DEFAULT_KABAN_DIR / 'config.toml'
                     )

# KABAN_DIR = Path.home() / '.kaban'

# TOML_FILE_PATH = KABAN_DIR / 'my_kaban_tasks.toml'
# YAML_FILE_PATH = KABAN_DIR / 'my_kaban_tasks.yaml'

# CONFIG_FILE_PATH = KABAN_DIR / 'config.toml'

