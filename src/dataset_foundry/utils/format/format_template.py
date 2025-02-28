from typing import Any, Dict, Optional

from .preprocess_template import preprocess_template

def format_template(
        template: str,
        variables: Dict[str, Any],
        formatters: Optional[Dict[str, callable]] = None,
    ) -> str:
    """
    Formats a template string with the given variables. Supports dotted references and
    custom formatting.

    Args:
        template (str): The template string to format.
        variables (dict): The variables to format the template with.
        formatters (Optional[dict]): A dictionary of formatters to use.

    Returns:
        str: The formatted template string.
    """
    template, variables = preprocess_template(template, variables, formatters)
    return template.format(**variables)
