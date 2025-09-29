import datason.json as json
import logging
from typing import Callable, Literal, Optional, Union
import yaml

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value
from ...utils.find_files import find_files

logger = logging.getLogger(__name__)

def load_dataset_from_directory(
        dir: Union[Callable,Key,str] = Key("context.input_dir"),
        include: Union[Callable,Key,str] = "*",
        exclude: Union[Callable,Key,str] = None,
        property: Union[Callable,Key,str] = None,
        format: Optional[Union[Callable,Literal['auto', 'text', 'json', 'yaml']]] = 'auto',
        merge: bool = False,
    ) -> DatasetAction:
    async def load_dataset_from_directory_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_include = resolve_dataset_value(include, dataset, context, required_as="include")
        resolved_exclude = resolve_dataset_value(exclude, dataset, context)
        resolved_property = resolve_dataset_value(property, dataset, context)
        resolved_format = resolve_dataset_value(format, dataset, context)

        include_path = resolved_dir / resolved_include
        exclude_path = resolved_dir / resolved_exclude if resolved_exclude else None
        file_infos = find_files(include_path, exclude_path)
        dataset_items = []

        logger.debug(f"Loading data from files matching {include_path}")

        for file_info in file_infos:
            if resolved_format == "auto":
                if file_info['path'].endswith((".yaml", ".yml")):
                    file_format = "yaml"
                elif file_info['path'].endswith(".json"):
                    file_format = "json"
                else:
                    file_format = "text"
            else:
                file_format = resolved_format

            with open(file_info['path']) as file:
                if file_format == "yaml":
                    data = yaml.safe_load(file)
                elif file_format == "json":
                    data = json.load(file)
                else:
                    data = file.read()

                dataset_items.append({
                    'data': data,
                    'metadata': file_info['metadata']
                })

        logger.debug(f"Loaded {len(dataset_items)} rows from {include_path}")

        if context['num_samples'] and len(dataset_items) > context['num_samples']:
            logger.debug(f"Limiting dataset to {context['num_samples']} samples")
            dataset_items = dataset_items[:context['num_samples']]

        for i, item_info in enumerate(dataset_items):
            data = item_info['data']
            metadata = item_info['metadata']

            # Merge metadata except for 'id' into data
            if isinstance(data, dict):
                data.update({
                    key: value for key, value in metadata.items() if key != 'id' and key not in data
                })

            if isinstance(data, dict) and 'id' in data:
                id = data['id']
                del data['id']
            else:
                id = metadata['id'] if 'id' in metadata else f"{i+1:03d}"

            item = DatasetItem(
                id=id,
                data={ resolved_property: data } if resolved_property else data
            )
            dataset.add(item, merge)

    return load_dataset_from_directory_action
