import logging
import os

from copy import deepcopy
from typing import Dict, Any

logger = logging.getLogger(__name__)

def resolve_environment_dict(environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve variables within an environment dict from the system environment. Variables should be
    in the form of ${VAR_NAME}.

    For example, here `LOGIN` will be resolved to the value of the `USER` environment variable:

    ```
    environment = resolve_environment_dict({
        "LOGIN": "${USER}"
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
            # Extract variable name and get from system environment
            var_name = value[2:-1]  # Remove ${ and }
            system_value = os.environ.get(var_name)

            if system_value:
                environment[key] = system_value
            else:
                # Pass through the expression as-is
                logger.warning(f"Environment variable {var_name} not found")

    return environment
