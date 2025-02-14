from pydantic import BaseModel
from typing import List

def get_model_fields(model: type[BaseModel]) -> List[str]:
    """Get a list of field descriptions from a Pydantic model.

    Args:
        model: A Pydantic BaseModel class

    Returns:
        List of strings in the format "field_name: field_description"

    Example:
        >>> get_model_fields(CodeSample)
        ['code: The code that needs refactoring',
         'language: The programming language of the code',
         'explanation: Explanation of why the code needs refactoring']
    """
    fields = []

    for name, field in model.model_fields.items():
        if field.description:
            fields.append(f"{name}: {field.description}")

    return fields