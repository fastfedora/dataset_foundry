from typing import Callable, Optional, Union

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.key import Key
from .resolve_value import resolve_value

def resolve_dataset_value(
        value: Union[Callable,Key,str,None],
        dataset: Dataset,
        context: Context,
        required_as: Optional[str] = None,
    ):
    """
    Resolve a value using a dataset and context. If `value` is callable, it will be called with the
    dataset and context as arguments. If `value` is a Key, it will be resolved using the dataset's
    metadata and the context. Otherwise, the value will be resolved as itself.

    If the value is a Template, it will be further resolved using the dataset's metadata and
    context, allowing for template strings like `{version}` or `{context.config_dir}`.

    Args:
        value: A function, key, or string that defines how to resolve the value.
        dataset: The dataset to use when resolving the value.
        context: The context to use when resolving the value.
        required_as: If set and the value is not found, an error will be raised using this parameter
            as the error message.

    Returns:
        The resolved value.
    """
    return resolve_value(value, dataset, dataset.metadata, context, required_as)
