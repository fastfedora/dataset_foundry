import json
import logging
from typing import Callable, Literal, Optional, Union
import yaml

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

logger = logging.getLogger(__name__)

def load_item(
        filename: Union[Callable,Key,str],
        dir: Union[Callable,Key,str] = Key("context.input_dir"),
        property: Union[Callable,Key,str] = None,
        format: Optional[Union[Callable,Literal['auto', 'text', 'json', 'yaml']]] = 'auto',
    ) -> ItemAction:
    async def load_item_action(item: DatasetItem, context: Context):
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_filename = resolve_item_value(filename, item, context, required_as="filename")
        resolved_property = resolve_item_value(property, item, context)
        resolved_format = resolve_item_value(format, item, context)

        if resolved_format == "auto":
            if resolved_filename.endswith(".yaml") or resolved_filename.endswith(".yml"):
                resolved_format = "yaml"
            elif resolved_filename.endswith(".json"):
                resolved_format = "json"

        path = resolved_dir / resolved_filename
        logger.debug(f"Loading data from {path}")
        with open(path) as file:
            if resolved_format == "yaml":
                contents = yaml.safe_load(file)
            elif resolved_format == "json":
                contents = json.load(file)
            else:
                contents = file.read()

        if resolved_property:
            item.push({ resolved_property: contents }, load_item)
        else:
            item.push(contents, load_item)

    return load_item_action
