import logging
from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...types.item_action import ItemAction
from ...utils.eval.item_eval import item_eval

logger = logging.getLogger(__name__)

def if_item(condition: str, if_actions: list, else_actions: list = []) -> ItemAction:
    """
    Creates an action that executes a list of actions if the given condition is met.

    Args:
        condition (str): A string representing the condition to evaluate.
        if_actions (list): A list of actions to execute if the condition is true.
        else_actions (list): A list of actions to execute if the condition is false.

    Returns:
        function: A function that takes a Dataset and Context and executes the corresponding
            actions based on the evaluated condition.
    """
    async def if_item_action(item: DatasetItem, context: Context):
        if item_eval(condition, item, context):
            logger.debug(f"Condition '{condition}' met. Executing 'if' actions.")
            for action in if_actions:
                await action(item, context)
        elif else_actions:
            logger.debug(f"Condition '{condition}' not met. Executing 'else' actions.")
            for action in else_actions:
                await action(item, context)
        else:
            logger.debug(f"Condition '{condition}' not met. No actions to execute.")

    return if_item_action