import logging
from typing import Callable, Union
import yaml

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value

logger = logging.getLogger(__name__)

# TODO: Rename this `load_dataset_from_file`
def load_dataset(
        filename: Union[Callable,Key,str] = "dataset.yaml",
        dir: Union[Callable,Key,str] = Key("context.input_dir"),
        property: Union[Callable,Key,str] = None,
        id_generator: Callable = lambda index, _data: f"{index+1:03d}",
    ) -> DatasetAction:
    async def load_dataset_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_file = resolve_dataset_value(filename, dataset, context, required_as="filename")
        resolved_property = resolve_dataset_value(property, dataset, context)

        path = resolved_dir / resolved_file
        logger.debug(f"Loading data from {path}")
        with open(path) as file:
            dataset_items = yaml.safe_load(file)

        if not isinstance(dataset_items, list):
            raise ValueError(f"The dataset at {path} must be a list")

        logger.debug(f"Loaded {len(dataset_items)} rows from {path}")

        if context['num_samples'] and len(dataset_items) > context['num_samples']:
            logger.debug(f"Limiting dataset to {context['num_samples']} samples")
            dataset_items = dataset_items[:context['num_samples']]

        for i, data in enumerate(dataset_items):
            item = DatasetItem(
                id=id_generator(i, data),
                data={ resolved_property: data } if resolved_property else data
            )
            dataset.add(item)

    return load_dataset_action
