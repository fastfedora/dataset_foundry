import logging
from typing import Callable, Union
import yaml
from pathlib import Path

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value
from ...utils.get import get

logger = logging.getLogger(__name__)

def save_dataset(
        filename: Union[Callable,Key,str] = "dataset.yaml",
        dir: Union[Callable,Key,str] = Key("context.output_dir"),
        property: Union[Callable,Key,str] = None,
    ) -> DatasetAction:
    async def save_dataset_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_file = resolve_dataset_value(filename, dataset, context, required_as="filename")
        resolved_property = resolve_dataset_value(property, dataset, context)

        # Create directory if it doesn't exist
        Path(resolved_dir).mkdir(parents=True, exist_ok=True)

        path = resolved_dir / resolved_file
        logger.debug(f"Saving dataset to {path}")

        if resolved_property:
            dataset_items = [
                get(item.data, resolved_property)
                for item in dataset.items
            ]
        else:
            dataset_items = [item.data for item in dataset.items]

        with open(path, 'w') as file:
            yaml.safe_dump(dataset_items, file, sort_keys=False)

        logger.debug(f"Saved {len(dataset_items)} items to {path}")

    return save_dataset_action