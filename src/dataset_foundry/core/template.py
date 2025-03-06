from typing import Any, Dict, Optional, Union

from ..utils.format.format_template import format_template

TemplateValue = Union[str, Dict[Any, Any]]

class Template:
    """
    An object that has strings, where each string may be a template with variables within curly
    braces. Variables can be referenced using dotted notation (e.g. `{item.data.name}`) and have
    custom formatters applied (e.g. `{item.data|yaml}`).
    """
    _value: TemplateValue

    @property
    def value(self) -> TemplateValue:
        return self._value

    def __init__(self, value: TemplateValue):
        """
        Initialize a new Template object.

        Args:
            value (TemplateValue): The value to be templated.
        """
        self._value = value

    def resolve(
            self,
            variables: Dict[str, Any],
            formatters: Optional[Dict[str, callable]] = None
        ) -> str:
        """
        Replace variables in the template with their corresponding values, applying the custom
        formatters if provided.

        If the template value is a string, then the string is resolved as a template. If the
        template value is a dict, then any key or value in the dict that is a Template is resolved
        as a template.

        Args:
            variables (dict): A dictionary of variables to replace in the template.
            formatters (Optional[dict]): A dictionary of formatters to apply to the variables. If
                not provided, the default formatters will be used: `yaml`, `json`, `upper`, `lower`.

        Returns:
            str: The template with variables replaced with their corresponding values.
        """
        if isinstance(self.value, str):
            return format_template(self.value, variables, formatters)
        elif isinstance(self.value, dict):
            resolved_value = {}

            for key, value in self.value.items():
                if isinstance(key, Template):
                    key = key.resolve(variables, formatters)

                if isinstance(value, Template):
                    value = value.resolve(variables, formatters)

                resolved_value[key] = value

            return resolved_value
        else:
            raise ValueError(f"Invalid type for template: {type(self.value)}")
