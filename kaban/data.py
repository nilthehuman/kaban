from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile
from tomlkit.exceptions import NonExistentKey

try:
    import yaml
except ImportError:
    pass  # oh well


@dataclass
class KabanTask:
    title: str
    date_added: datetime
    date_last_logged: Optional[datetime] = None
    recurring: Optional[str] = None
    notes: Optional[str] = None
    estimate: Optional[timedelta] = None
    done: timedelta = timedelta(0)
    #color: None  # TODO eventually


class KabanBag(KabanTask, list):
    pass


class KabanData(list):
    """The Python class corresponding to the contents of a kaban YAML or TOML file."""

    def __init__(self):
        self.toml_document = None
        self.last_task = None
        self.tasks = None

    def load_from_file(self, filepath, format='toml'):
        if format == 'toml':
            self.toml_document = TOMLFile(filepath).read()
        elif format == 'yaml':
            with open(filepath, 'r', encoding='utf-8') as file:
                self.yaml_document = yaml.safe_load(file)
        else:
            assert False
        try:
            # process top-level tasks
            for task in self.toml_document['tasks']:
                self.append(KabanTask(**task))
        except NonExistentKey:
            pass  # no top-level tasks found
        # process bags
        try:
            for bag in self.toml_document['bags']:
                try:
                    self.append(KabanBag(**bag))
                except TypeError as te:
                    # this must be a subarray below the 'bags' array
                    pass  # TODO
        except NonExistentKey:
            pass  # no bags found
        print("good so far:")
        print(self)

