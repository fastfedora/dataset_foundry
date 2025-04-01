from datetime import datetime
from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

def get_pipeline_metadata(context: Context) -> dict:
    parent_metadata = get_pipeline_metadata(context.parent) if context.parent else None

    return {
        "name": context.pipeline.name,
        **context.pipeline.metadata,
        **({ "parent": parent_metadata } if parent_metadata else {}),
    }

def set_item_metadata(
        property: Union[Callable,Key,str] = "metadata",
    ) -> ItemAction:
    async def set_item_metadata_action(item: DatasetItem, context: Context):
        resolved_property = resolve_item_value(property, item, context, required_as="property")

        metadata = {
            "pipeline": get_pipeline_metadata(context),
            "model": context.model.info,
            "created_at": datetime.now().isoformat(),
        }

        item.push({
            resolved_property: metadata
        }, set_item_metadata);

    return set_item_metadata_action
