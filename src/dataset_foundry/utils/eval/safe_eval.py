from typing import Optional

from ..filesystem.path_exists import path_exists

ALLOWED_GLOBALS = ['len', 'list', 'dict']

DEFAULT_FUNCTIONS = {
    'path_exists': path_exists,
}

def safe_eval(
        expression: str,
        locals: dict = {},
        functions: Optional[dict] = None,
        allowed_globals: Optional[list] = ALLOWED_GLOBALS,
    ):
    if functions is None:
        functions = DEFAULT_FUNCTIONS

    safe_globals = {
        "__builtins__": {
            name: __builtins__[name]
            for name in allowed_globals
        },
        **functions,
    }

    return eval(expression, safe_globals, locals)
