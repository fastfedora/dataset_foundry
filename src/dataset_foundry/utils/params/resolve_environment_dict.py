import logging
import os

from copy import deepcopy
from typing import Dict, Any

logger = logging.getLogger(__name__)

def resolve_environment_dict(environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve variables within an environment dict from the system environment. Variables should be
    in the form of `${VAR_NAME}`. Default values can be provided by using the format
    `${VAR_NAME:-default_value}`.

    For example, here `LOGIN` will be resolved to the value of the `USER` environment variable, or
    `root` if the `USER` environment variable is not set:

    ```
    environment = resolve_environment_dict({
        "LOGIN": "${USER:-root}"
    })
    ```

    Args:
        environment (Dict[str, Any]): The environment dictionary to resolve.

    Returns:
        Dict[str, Any]: The resolved environment dictionary.
    """
    if not environment or not isinstance(environment, dict):
        return environment

    # Ensure we don't modify the original environment dictionary
    environment = deepcopy(environment)

    for key, value in environment.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            inner = value[2:-1]  # Remove ${ and }
            if ':-' in inner:
                var_name, default_value = inner.split(':-', 1)
            else:
                var_name, default_value = inner, None
            system_value = os.environ.get(var_name)

            if system_value is not None and system_value != "":
                environment[key] = system_value
            elif default_value is not None and default_value != "":
                environment[key] = default_value
            else:
                # Pass through the expression as-is
                logger.warning(f"Environment variable {var_name} not found and no default provided")

    return environment
