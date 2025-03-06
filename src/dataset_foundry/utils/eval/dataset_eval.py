from typing import Optional

from ...core.context import Context
from ...core.dataset import Dataset
from .safe_eval import safe_eval

def dataset_eval(
        expression: str,
        dataset: Dataset,
        context: Context,
        variables: dict = {},
        functions: Optional[dict] = None,
    ):
    locals = {
        **variables,
        **dataset.metadata,
        'dataset': dataset,
        'context': context,
    }

    return safe_eval(expression, locals, functions)
