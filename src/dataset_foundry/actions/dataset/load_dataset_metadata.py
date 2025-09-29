import datason.json as json
import logging
from typing import Callable, Union
import yaml

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value

logger = logging.getLogger(__name__)

def load_dataset_metadata(
        filename: Union[Callable,Key,str] = "metadata.yaml",
        dir: Union[Callable,Key,str] = Key("context.input_dir"),
        property: Union[Callable,Key,str] = None,
    ) -> DatasetAction:
    async def load_dataset_metadata_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_file = resolve_dataset_value(filename, dataset, context, required_as="filename")
        resolved_property = resolve_dataset_value(property, dataset, context)

        path = resolved_dir / resolved_file
        logger.debug(f"Loading metadata from {path}")

        with open(path) as file:
            if path.suffix == ".json":
                metadata = json.load(file)
            elif path.suffix == ".yaml" or path.suffix == ".yml":
                metadata = yaml.safe_load(file)
            else:
                metadata = file.read()

        if resolved_property:
            dataset.metadata = { resolved_property: metadata }
        else:
            dataset.metadata = metadata

    return load_dataset_metadata_action
