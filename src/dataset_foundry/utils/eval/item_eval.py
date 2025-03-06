from typing import Optional

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from .safe_eval import safe_eval

def item_eval(
        expression: str,
        item: DatasetItem,
        context: Context,
        variables: dict = {},
        functions: Optional[dict] = None,
    ):
    locals = {
        **variables,
        **item.data,
        'id': item.id,
        'context': context,
    }

    return safe_eval(expression, locals, functions)
