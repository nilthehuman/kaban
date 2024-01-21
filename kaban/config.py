from dataclasses import dataclass, asdict

from tomlkit import comment
from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile


import kaban.defaults as defaults


@dataclass
class KabanConfig:

    format: str = 'toml'
    local: bool = False
    quiet: bool = False

    def __setattr__(self, attr, value):
        """Write every change to file automatically."""
        super().__setattr__(attr, value)
        self.save_to_file()

    def load_from_file(self, filename):
        """Destructively load all config options from the config file."""
        # sic, because KabanControl.__init__ may pass us an explicit None argument
        if filename is None:
            filename = defaults.CONFIG_FILE_PATH
        toml_document = TOMLFile(filename).read()
        for attr_name in toml_document:
            assert hasattr(self, attr_name)
            setattr(self, attr_name, toml_document[attr_name])

    def save_to_file(self, filename=defaults.CONFIG_FILE_PATH):
        """Serialize and write all current settings to file."""
        toml_document = TOMLDocument()
        toml_document.add(comment('kaban config file, edit at your own risk'))
        config_dict = asdict(self)
        for attr_name in config_dict:
            toml_document.append(attr_name, config_dict[attr_name])
        TOMLFile(filename).write(toml_document)

