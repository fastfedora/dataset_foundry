import datason.json as json
from pathlib import Path
import yaml

from mergedeep import merge

class Config(dict):
    """
    A object to store configuration values.

    Supports referencing other keys in the config file within the string values of other keys using
    the `{#key}` syntax. For instance, if the `criteria` key has the value `"only words"`, then the
    key `prompt` with the value `"Search for {#criteria}"` resolves to `"Search for only words"`.
    Variable placeholders that aren't prefixed with `#` remain untouched. If a value is not a
    string, it will be formatted as a YAML string before being substituted.

    To reference a nested key, use the dot notation.

    Supports an `include` key that contains a list of additional config files to load and merge.
    Include paths are resolved relative to the config file containing the include. The main config
    file's values take precedence over included files, and later includes override earlier ones.
    """
    def __init__(self, path_or_values: Path | str | dict):
        super().__init__()

        if isinstance(path_or_values, dict):
            values = path_or_values
        else:
            config_path = Path(path_or_values)
            values = self._load_file(config_path)

        self.update(values)
        self._resolve_anchors(values)

    def _load_file(self, path: Path) -> dict:
        """
        Load a JSON or YAML file and return its contents as a dict. If the file contains an
        `include` key, process the includes relative to the file's directory.
        """
        with open(path) as file:
            if path.suffix == ".json":
                values = json.load(file)
            else:
                values = yaml.safe_load(file)

        if "include" in values:
            values = self._process_includes(values, path.parent)

        return values

    def _process_includes(self, values: dict, base_directory: Path) -> dict:
        """
        Process the include key, loading and merging additional config files.
        Include paths are resolved relative to the base_directory.
        """
        include_paths = values.pop("include")
        result = {}

        for include_path in include_paths:
            included_values = self._load_file(base_directory / include_path)
            # Merge included values into result (later includes override earlier ones)
            merge(result, included_values)

        # Merge main config values last (main config takes precedence)
        merge(result, values)
        return result


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
