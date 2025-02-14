from typing import Callable, Union
import yaml

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.key import Key
from ...utils.params.resolve_dataset_value import resolve_dataset_value

def load_context(
        filename: Union[Callable,Key,str] = "config.yaml",
        dir: Union[Callable,Key,str] = Key("config_dir"),
    ):
    async def load_context_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_file = resolve_dataset_value(filename, dataset, context, required_as="filename")

        path = resolved_dir / resolved_file
        with open(path) as file:
            config = yaml.safe_load(file)
            context.update(**config)

    return load_context_action
