import importlib
from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.item_pipeline import ItemPipeline
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_item_value import resolve_item_value

def do_item_steps(
        pipeline: Union[Callable,Key,ItemPipeline,str],
    ) -> DatasetAction:
    async def do_item_steps_action(item: DatasetItem, context: Context):
        resolved_pipeline = resolve_item_value(pipeline, item, context, required_as="pipeline")

        if isinstance(resolved_pipeline, str):
            resolved_pipeline = importlib.import_module(resolved_pipeline).pipeline

        if isinstance(resolved_pipeline, ItemPipeline):
            await resolved_pipeline.process_data_item(item, context.create_child(resolved_pipeline))
        else:
            raise ValueError(f"The pipeline {resolved_pipeline} is not a valid item pipeline")

    return do_item_steps_action
