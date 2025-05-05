import ast
from typing import Callable, Optional, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

def validate_code_syntax(
        input: Optional[Union[Callable,Key,str]] = Key("output"),
        output_key: Optional[Union[Callable,Key,str]] = "code_syntax",
    ) -> ItemAction:

    async def validate_code_syntax_action(item: DatasetItem, context: Context):
        resolved_input = resolve_item_value(input, item, context, required_as="input")
        resolved_output_key = resolve_item_value(output_key, item, context)

        try:
            ast.parse(resolved_input)
            is_valid = True
            syntax_error = None
        except SyntaxError as e:
            is_valid = False
            syntax_error = str(e)

        result = {
            "is_valid": is_valid,
            "syntax_error": syntax_error
        }

        if resolved_output_key:
            item.push({ resolved_output_key: result }, validate_code_syntax)
        else:
            item.push(result, validate_code_syntax)

    return validate_code_syntax_action