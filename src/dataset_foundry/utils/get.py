from typing import Any, Union, Sequence
from functools import reduce

def get(obj: Any, path: Union[str, Sequence[str]], default: Any = None) -> Any:
    """
    Access nested dictionary items or object attributes using a path string or sequence.

    Args:
        obj: The object or dictionary to traverse
        path: Either a dot-separated string ('a.b.c') or sequence of keys/attrs ['a', 'b', 'c']
        default: Value to return if path doesn't exist

    Returns:
        The value at the path or the default value if not found

    Examples:
        >>> data = {'a': {'b': {'c': 1}}}
        >>> get_in(data, 'a.b.c')
        1
        >>> get_in(data, ['a', 'b', 'c'])
        1

        >>> class Obj: pass
        >>> o = Obj()
        >>> o.a = {'b': 3}
        >>> get_in(o, 'a.b')
        3
    """
    if isinstance(path, str):
        path = path.split('.')

    try:
        return reduce(lambda d, key: getattr(d, key, None) if hasattr(d, key)
                     else d.get(key) if hasattr(d, 'get')
                     else d[key] if hasattr(d, '__getitem__') and key in d
                     else None, path, obj)
    except (AttributeError, KeyError, TypeError):
        return default