from typing import Optional, Union, Callable
import logging
import asyncio

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...core.template import Template
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

logger = logging.getLogger(__name__)


def log_counter(
        start: int = 1,
        count: int = 1,
        interval: int = 1000,
        message: Optional[Union[Callable, Key, str, Template]] = None,
    ) -> ItemAction:
    """
    Log a message repeatedly, once per interval, for a given count. Use for debugging async
    pipelines.

    Args:
        start: The starting value for the counter (inclusive).
        count: The number of times to log the message.
        interval: The time between logs, in milliseconds.
        message: A message to log. May be a callable, key, string, or Template.
                 When a Template is provided, it can reference `{count}` which
                 will be the current counter value for that iteration.
    """
    async def log_counter_action(item: DatasetItem, context: Context):
        for i in range(count):
            current_count = start + i

            if isinstance(message, Template):
                variables = { **item.data, 'context': context }
                if hasattr(item, 'id'):
                    variables['id'] = item.id
                variables['count'] = current_count
                resolved_message = message.resolve(variables)
            elif message is not None:
                # Fall back to generic resolver (does not inject `count`)
                resolved_message = resolve_item_value(message, item, context)
            else:
                resolved_message = None

            output = resolved_message if resolved_message is not None else f"[{item.id}] {current_count}"
            logger.info(output)

            if i < count - 1:
                await asyncio.sleep(max(0, interval) / 1000.0)

    return log_counter_action
