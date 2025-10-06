import logging
from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

logger = logging.getLogger(__name__)

def foreach_item_element(
        collection: Union[Callable, Key, list, tuple],
        actions: list,
    ) -> ItemAction:
    """
    Creates an action that executes a list of actions on each element in a collection belonging to
    the current item.

    Args:
        collection (Union[Callable, Key, list, tuple]): The collection to iterate over.
        actions (list): A list of actions to execute for each element in the collection.

    Returns:
        function: A function that takes a DatasetItem and Context and executes the actions
            for each element in the collection belonging to the current item.
    """
    async def foreach_item_element_action(item: DatasetItem, context: Context):
        resolved_collection = resolve_item_value(collection, item, context)

        if not isinstance(resolved_collection, (list, tuple)):
            raise ValueError("'collection' is not iterable; it must resolve to a list or tuple")

        logger.debug(f"Executing foreach over {len(resolved_collection)} items")

        for index, element in enumerate(resolved_collection):
            element_item = DatasetItem(
                id=f"{item.id}_{index}",
                data={
                    'parent': item,
                    'index': index,
                    'element': element,
                }
            )

            for action in actions:
                await action(element_item, context)

            # TODO: Maybe store the result of any changes to `element` in the item data. If so,
            #       save a copy of `element` in the `DataItem` above. [fastfedora 14.Jul.25]

    return foreach_item_element_action