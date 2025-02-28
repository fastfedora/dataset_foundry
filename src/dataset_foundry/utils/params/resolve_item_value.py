from typing import Callable, Optional, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from .resolve_value import resolve_value

def resolve_item_value(
        value: Union[Callable,Key,str,None],
        item: DatasetItem,
        context: Context,
        required_as: Optional[str] = None,
    ):
    """
    Resolve a value using a data item and context. If `value` is callable, it will be called with
    the data item and context as arguments. If `value` is a Key, it will be resolved using the data
    item's data and the context. Otherwise, the value will be resolved as itself.

    If the value is a Template, it will be further resolved using the item's id, data and context,
    allowing for template strings like `{id}`, `{spec.name}` or `{context.config_dir}`.

    Args:
        value: A function, key, or string that defines how to resolve the value.
        item: The data item to use when resolving the value.
        context: The context to use when resolving the value.
        required_as: If set and the value is not found, an error will be raised using this parameter
            as the error message.

    Returns:
        The resolved value.
    """
    return resolve_value(value, item, item.data, context, required_as)
