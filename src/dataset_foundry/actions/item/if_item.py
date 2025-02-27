import logging

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...types.item_action import ItemAction

logger = logging.getLogger(__name__)

def if_item(condition: str, actions: list) -> ItemAction:
    """
    Creates an action that executes a list of actions if the given condition is met.

    Args:
        condition (str): A string representing the condition to evaluate.
        actions (list): A list of actions to execute if the condition is true.

    Returns:
        function: A function that takes a Dataset and Context and executes the actions if the
            condition is true.
    """
    async def if_item_action(item: DatasetItem, context: Context):
        if eval(condition, {}, {'item': item, 'context': context}):
            logger.debug(f"Condition '{condition}' met. Executing actions.")
            for action in actions:
                await action(item, context)
        else:
            logger.debug(f"Condition '{condition}' not met. Skipping actions.")

    return if_item_action