from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.unit_tests.run_python_unit_tests import run_python_unit_tests

def run_unit_tests(
        filename: Union[Callable,Key,str],
        dir: Union[Callable,Key,str] = Key("input_dir"),
        prefix: Union[Callable,Key,str] = "test_",
    ):
    async def run_unit_tests_action(item: DatasetItem, context: Context):
        resolved_filename = resolve_item_value(filename, item, context, required_as="filename")
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_prefix = resolve_item_value(prefix, item, context, required_as="prefix")

        if isinstance(resolved_filename, str):
            format_data = {**item.data, 'id': item.id}
            resolved_filename = resolved_filename.format(**format_data)

        result = run_python_unit_tests(resolved_dir / resolved_filename)

        item.push({
            f"{resolved_prefix}returncode": result.returncode,
            f"{resolved_prefix}stdout": result.stdout,
            f"{resolved_prefix}stderr": result.stderr,
        }, run_unit_tests)

    return run_unit_tests_action
