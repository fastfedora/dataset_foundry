import logging
from ...core.context import Context
from ...core.dataset import Dataset
from ...types.dataset_action import DatasetAction
from ...utils.eval.dataset_eval import dataset_eval

logger = logging.getLogger(__name__)

def if_dataset(condition: str, actions: list) -> DatasetAction:
    """
    Creates an action that executes a list of dataset actions if the given condition is met.

    Args:
        condition (str): A string representing the condition to evaluate.
        actions (list): A list of dataset actions to execute if the condition is true.

    Returns:
        function: A function that takes a Dataset and Context and executes the actions if the
            condition is true.
    """
    async def if_dataset_action(dataset: Dataset, context: Context):
        if dataset_eval(condition, dataset, context):
            logger.debug(f"Condition '{condition}' met. Executing actions.")
            for action in actions:
                await action(dataset, context)
        else:
            logger.debug(f"Condition '{condition}' not met. Skipping actions.")

    return if_dataset_action