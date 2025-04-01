from typing import Callable, Optional, Union, Literal
import json
import yaml

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.format.format_template import format_template

def save_item(
        filename: Union[Callable,Key,str],
        contents: Optional[Union[Callable,Key,str]] = None,
        dir: Union[Callable,Key,str] = Key("context.output_dir"),
        format: Optional[Union[Callable,Literal['auto', 'text', 'json', 'yaml']]] = 'auto',
    ) -> ItemAction:

    async def save_item_action(item: DatasetItem, context: Context):
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_filename = resolve_item_value(filename, item, context, required_as="filename")
        resolved_contents = resolve_item_value(contents, item, context) or item.data
        resolved_format = resolve_item_value(format, item, context)

        if resolved_format == "auto":
            if resolved_filename.endswith(".yaml") or resolved_filename.endswith(".yml"):
                resolved_format = "yaml"
            elif resolved_filename.endswith(".json"):
                resolved_format = "json"

        if resolved_format == 'json':
            resolved_contents = json.dumps(resolved_contents, indent=2)
        elif resolved_format == 'yaml':
            resolved_contents = yaml.dump(resolved_contents, sort_keys=False, width=100)
        else:
            resolved_contents = str(resolved_contents)

        path = resolved_dir / resolved_filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(resolved_contents)

    return save_item_action
