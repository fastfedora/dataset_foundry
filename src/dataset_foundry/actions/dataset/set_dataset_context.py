from ...core.dataset import Dataset
from ...core.context import Context
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value

def set_dataset_context(
        **kwargs,
    ) -> DatasetAction:
    async def set_dataset_context_action(dataset: Dataset, context: Context):
        for key, value in kwargs.items():
            context[key] = resolve_dataset_value(value, dataset, context)

    return set_dataset_context_action
