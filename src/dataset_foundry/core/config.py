import json
from pathlib import Path
import yaml

class Config(dict):
    """
    A object to store configuration values.
    """
    def __init__(self, pathOrValues: Path|str|dict):
        super().__init__()

        if not isinstance(pathOrValues, dict):
            with open(pathOrValues) as file:
                if pathOrValues.suffix == ".json":
                    values = json.load(file)
                else:
                    values = yaml.safe_load(file)
        else:
            values = pathOrValues

        self.update(values)
