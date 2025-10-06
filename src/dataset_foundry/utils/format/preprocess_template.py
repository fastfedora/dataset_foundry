import re
import yaml
import datason.json as json
from typing import Any, Dict, Tuple, Optional

from ...utils.get import get

DEFAULT_FORMATTERS = {
    "yaml": lambda v: yaml.dump(v, default_flow_style=False, sort_keys=False, width=100),
    "json": lambda v: json.dumps(v, indent=2),
    "upper": lambda v: str(v).upper(),
    "lower": lambda v: str(v).lower()
}

def preprocess_template(
        template: str,
        variables: Dict[str, Any],
        formatters: Optional[Dict[str, callable]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
    """
    Preprocesses a template by handling both dotted paths and formatters in variables.

    Supports:
    - Dotted paths: {var.subkey}
    - Formatters: {var:format}
    - Combined: {var.subkey:format}

    Args:
        template (str): The input template with placeholders.
        variables (dict): The input variables to be formatted.
        formatters (Optional[dict]): A mapping of format names to formatting functions.

    Returns:
        Tuple[str, Dict[str, Any]]: A new template with transformed variable names and updated
            values.
    """
    if formatters is None:
        formatters = DEFAULT_FORMATTERS

    new_variables = variables.copy()

    def replace_variable(match):
        """Handles both dotted paths and formatters in a single pass."""
        var_path = match.group(1)  # Extract "var.subkey" or "var"
        format_type = match.group(2)  # Extract format type if present

        # Get the value, handling dotted paths
        value = get(variables, var_path)
        if value is None:
            return match.group(0)  # Leave unchanged if not found

        # Generate new variable name
        var_name = var_path.replace(".", "_")

        # Apply formatter if present
        if format_type and format_type in formatters:
            var_name = f"{var_name}__{format_type}"
            value = formatters[format_type](value)

        new_variables[var_name] = value
        return f"{{{var_name}}}"

    # Handle both {var.subkey} and {var.subkey:format} in a single pass
    template = re.sub(r"{([\w.]+)(?::(\w+))?}", replace_variable, template)

    return template, new_variables
