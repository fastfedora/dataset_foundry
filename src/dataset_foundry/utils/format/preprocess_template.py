import re
import yaml
import json
from typing import Any, Dict, Tuple, Optional

from ...utils.get import get

DEFAULT_FORMATTERS = {
    "yaml": lambda v: yaml.dump(v, default_flow_style=False, sort_keys=False),
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
    Preprocesses a template by:

    1. Resolving `{var.subkey}` to `{var_subkey}`.
    2. Applying custom formatting `{var:format}` → `{var__format}`.

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

    # Handle dotted references {var.subkey}
    def replace_dotted(match):
        """Replaces `{var.subkey}` with `{var_subkey}` and retrieves its value."""
        var_path = match.group(1)  # Extract "var.subkey"
        var_name = var_path.replace(".", "_")  # Convert "var.subkey" -> "var_subkey"

        value = get(variables, var_path)
        if value is not None:
            new_variables[var_name] = value
            return f"{{{var_name}}}"
        return match.group(0)  # Leave unchanged if not found

    # Handle `{var:format}` transformations
    def replace_format(match):
        """Replaces `{var:format}` with `{var_format}` and applies formatting."""
        var_name, format_type = match.groups()
        if var_name in new_variables and format_type in formatters:
            new_var_name = f"{var_name}__{format_type}"
            new_variables[new_var_name] = formatters[format_type](new_variables[var_name])
            return f"{{{new_var_name}}}"
        return match.group(0)  # Leave unchanged if no formatter found

    # First, replace `{var.subkey}`
    template = re.sub(r"{([\w.]+)}", replace_dotted, template)

    # Then, replace `{var:format}`
    template = re.sub(r"{(\w+):(\w+)}", replace_format, template)

    return template, new_variables
