import logging
from toolz import get_in
from typing import Any, Callable, Optional, Union

from ...core.context import Context
from ...core.key import Key
from ...core.template import Template

logger = logging.getLogger(__name__)

def resolve_value(
        value: Union[Callable,Key,str,None],
        object: Any,
        data: dict,
        context: Context,
        required_as: Optional[str] = None,
    ):
    resolved_value = None

    if value:
        if callable(value):
            arg_count = value.__code__.co_argcount
            if arg_count == 1:
                resolved_value = value(object)
            else:
                resolved_value = value(object, context)
        elif isinstance(value, Key):
            path = value.path.split('.')
            for source in [data, context]:
                resolved_value = get_in(path, source)
                if resolved_value is not None:
                    break
            if resolved_value is None:
                resolved_value = None
        else:
            resolved_value = value

    if required_as and not resolved_value:
        raise ValueError(f"'{required_as}' must be passed in or defined in the metadata or context")

    logger.debug(
        f"Resolved '{value.path if isinstance(value, Key) else value}' to '{resolved_value}'"
    )

    if isinstance(resolved_value, Template):
        variables = { **data, 'context': context }
        if hasattr(object, 'id'):
            variables['id'] = object.id
        resolved_value = resolved_value.resolve(variables)

    return resolved_value
