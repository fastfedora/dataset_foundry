from typing import List, Optional
from pprint import pformat
import logging

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...utils.get import get

logger = logging.getLogger(__name__)

def log_item(
        properties: Optional[List[str]] = None
    ):
    async def log_item_action(item: DatasetItem, _context: Context):
        if properties:
            if len(properties) == 1:
                message = f"[{item.id}] {properties[0]}: {get(item.data, properties[0])}"
            else:
                filtered_data = {
                    key: get(item.data, key.split('.')) for key in properties
                }
                message = f"[{item.id}] {pformat(filtered_data)}"
        else:
            message = f"[{item.id}] {pformat(item.data)}"

        logger.info(message)

    return log_item_action
