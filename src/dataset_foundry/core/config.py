import datason.json as json
from pathlib import Path
import yaml

class Config(dict):
    """
    A object to store configuration values.

    Supports referencing other keys in the config file within the string values of other keys using
    the `{#key}` syntax. For instance, if the `criteria` key has the value `"only words"`, then the
    key `prompt` with the value `"Search for {#criteria}"` resolves to `"Search for only words"`.
    Variable placeholders that aren't prefixed with `#` remain untouched. If a value is not a
    string, it will be formatted as a YAML string before being substituted.

    To reference a nested key, use the dot notation.
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
        self._resolve_anchors(values)

    def _resolve_anchors(self, data):
        """
        Recursively resolves anchor references in the configuration data.
        Anchor references are in the format {#key.subkey} and will be replaced
        with the corresponding value from the configuration.
        """
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, str):
                    data[key] = self._replace_anchors_in_string(value)
                else:
                    self._resolve_anchors(value)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, str):
                    data[index] = self._replace_anchors_in_string(item)
                else:
                    self._resolve_anchors(item)

    def _replace_anchors_in_string(self, value):
        """
        Replaces anchor references in a string with their corresponding values.
        """
        import re
        pattern = re.compile(r'\{#(.*?)\}')
        matches = pattern.findall(value)

        for match in matches:
            anchor_value = self._get_nested_value(match, self)
            if anchor_value is not None:
                if not isinstance(anchor_value, str):
                    anchor_value = yaml.dump(anchor_value).strip()
                value = value.replace(f'{{#{match}}}', anchor_value)

        return value

    def _get_nested_value(self, key_path, data):
        """
        Retrieves a nested value from the data dictionary using a dot-separated key path.
        """
        keys = key_path.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value
