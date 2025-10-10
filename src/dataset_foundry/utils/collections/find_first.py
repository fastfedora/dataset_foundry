from typing import Callable, Iterable


def find_first[T](
    iterable: Iterable[T],
    predicate: Callable[[T], bool],
    default: T | None = None
) -> T | None:
    """
    Return the first element in `iterable` that matches `predicate`, or `default` if none.
    """
    for element in iterable:
        if predicate(element):
            return element
    return default
