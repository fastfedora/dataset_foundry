from typing import Any, Dict, Optional

from ..utils.format.format_template import format_template

class Template:
    """
    A string containing a template with variables within curly braces. Variables can be
    referenced using dotted notation (e.g. `{item.data.name}`) and have custom formatters applied
    (e.g. `{item.data|yaml}`).
    """
    _value: str

    @property
    def value(self) -> str:
        return self._value

    def __init__(self, value: str):
        self._value = value

    def resolve(
            self,
            variables: Dict[str, Any],
            formatters: Optional[Dict[str, callable]] = None
        ) -> str:
        """
        Replace variables in the template with their corresponding values, applying the custom
        formatters if provided.

        Args:
            variables (dict): A dictionary of variables to replace in the template.
            formatters (Optional[dict]): A dictionary of formatters to apply to the variables. If
                not provided, the default formatters will be used: `yaml`, `json`, `upper`, `lower`.

        Returns:
            str: The template with variables replaced with their corresponding values.
        """
        return format_template(self.value, variables, formatters)
