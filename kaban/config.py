from dataclasses import dataclass, asdict

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile


import kaban.defaults as defaults


@dataclass
class KabanConfig:

    format: str = 'toml'
    local: bool = False
    quiet: bool = False

    def load_from_file(self, filename):
        # sic: KabanControl.__init__ may pass us an explicit None argument
        if filename is None:
            filename = defaults.CONFIG_FILE_PATH
        toml_document = TOMLFile(filename).read()
        for key, value in toml_document:
            assert hasattr(self, key)
            setattr(self, key, value)

    def save_to_file(self, filename=defaults.CONFIG_FILE_PATH):
        toml_document = TOMLDocument()
        for key, value in asdict(self):
            print(key, value)
            toml_document.append(key, value)
        print(toml_document)
        TOMLFile(filename).write(toml_document)

