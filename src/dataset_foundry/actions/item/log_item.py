from typing import List, Optional
from pprint import pformat
import logging

from ...core.context import Context
from ...core.dataset_item import DatasetItem

logger = logging.getLogger(__name__)

def log_item(
        properties: Optional[List[str]] = None
    ):
    async def log_item_action(item: DatasetItem, _context: Context):
        if properties:
            if len(properties) == 1:
                logger.info(f"[{item.id}] {properties[0]}: {item.data[properties[0]]}")
            else:
                filtered_data = {
                    key: value for key, value in item.data.items() if key in properties
                }
                logger.info(f"[{item.id}] {pformat(filtered_data)}")
        else:
            logger.info(f"[{item.id}] {pformat(item.data)}")

    return log_item_action
