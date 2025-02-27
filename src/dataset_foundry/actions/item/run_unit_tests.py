from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.unit_tests.run_python_unit_tests import run_python_unit_tests
from ...utils.format.format_template import format_template

def run_unit_tests(
        filename: Union[Callable,Key,str],
        dir: Union[Callable,Key,str] = Key("input_dir"),
        property: Union[Callable,Key,str] = "test_result",
    ) -> ItemAction:
    async def run_unit_tests_action(item: DatasetItem, context: Context):
        resolved_filename = resolve_item_value(filename, item, context, required_as="filename")
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_property = resolve_item_value(property, item, context, required_as="property")

        if isinstance(resolved_dir, str):
            format_data = {**item.data, 'id': item.id}
            resolved_dir = format_template(resolved_dir, format_data)

        if isinstance(resolved_filename, str):
            format_data = {**item.data, 'id': item.id}
            resolved_filename = format_template(resolved_filename, format_data)

        result = run_python_unit_tests(resolved_dir / resolved_filename)

        item.push({ resolved_property: result }, run_unit_tests)

    return run_unit_tests_action
