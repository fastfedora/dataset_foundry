import logging
from ...core.context import Context
from ...core.dataset import Dataset
from ...types.dataset_action import DatasetAction
from ...utils.eval.dataset_eval import dataset_eval

logger = logging.getLogger(__name__)

def if_dataset(condition: str, if_actions: list, else_actions: list = None) -> DatasetAction:
    """
    Creates an action that executes a list of dataset actions if the given condition is met.

    Args:
        condition (str): A string representing the condition to evaluate.
        if_actions (list): A list of dataset actions to execute if the condition is true.
        else_actions (list): A list of dataset actions to execute if the condition is false.

    Returns:
        function: A function that takes a Dataset and Context and executes the actions if the
            condition is true.
    """
    async def if_dataset_action(dataset: Dataset, context: Context):
        if dataset_eval(condition, dataset, context):
            logger.debug(f"Condition '{condition}' met. Executing 'if' actions.")
            for action in if_actions:
                await action(dataset, context)
        elif else_actions:
            logger.debug(f"Condition '{condition}' not met. Executing 'else' actions.")
            for action in else_actions:
                await action(dataset, context)
        else:
            logger.debug(f"Condition '{condition}' not met. No actions to execute.")

    return if_dataset_action