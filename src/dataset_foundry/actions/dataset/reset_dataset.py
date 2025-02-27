from ...core.context import Context
from ...core.dataset import Dataset
from ...types.dataset_action import DatasetAction

def reset_dataset() -> DatasetAction:
    async def reset_dataset_action(dataset: Dataset, _context: Context):
        dataset.reset()

    return reset_dataset_action
