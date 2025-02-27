from typing import List, Optional, Union, Callable
from pprint import pformat
import logging

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.get import get
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.format.format_template import format_template

logger = logging.getLogger(__name__)

def log_item(
        properties: Optional[List[str]] = None,
        message: Optional[Union[Callable,Key,str]] = None,
    ) -> ItemAction:
    async def log_item_action(item: DatasetItem, context: Context):
        resolved_message = resolve_item_value(message, item, context)

        if isinstance(resolved_message, str):
            format_data = {**item.data, 'id': item.id}
            resolved_message = format_template(resolved_message, format_data)

        if (resolved_message):
            if properties:
                raise ValueError("'properties' and 'message' cannot both be provided")

            logger.info(resolved_message)
        else:
            if properties:
                if len(properties) == 1:
                    output = f"[{item.id}] {properties[0]}: {get(item.data, properties[0])}"
                else:
                    filtered_data = {
                        key: get(item.data, key.split('.')) for key in properties
                    }
                    output = f"[{item.id}] {pformat(filtered_data)}"
            else:
                output = f"[{item.id}] {pformat(item.data)}"

            logger.info(output)

    return log_item_action
