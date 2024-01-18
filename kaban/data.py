from dataclasses import dataclass

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile

try:
    import yaml
except ImportError:
    pass  # oh well


@dataclass
class KabanTask:
    pass


class KabanData:
    """The Python class corresponding to the contents of a kaban YAML or TOML file."""

    def __init__(self):
        self.toml_document = None

    def load_from_file(self, filename, format='toml'):
        if format == 'toml':
            self.toml_document = TOMLFile(filename).read()
        elif format == 'yaml':
            with open(filename, 'r', encoding='utf-8') as file:
                self.yaml_document = yaml.safe_load(file)
        else:
            assert False

