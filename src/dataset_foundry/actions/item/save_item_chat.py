from typing import Callable, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.save_messages import save_messages
from ...utils.format.format_template import format_template

def save_item_chat(
        dir: Union[Callable,Key,str] = Key("log_dir"),
        filename: Union[Callable,Key,str] = "log.yaml",
    ):
    async def save_item_chat_action(item: DatasetItem, context: Context):
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_filename = resolve_item_value(filename, item, context, required_as="filename")

        if isinstance(resolved_filename, str):
            format_data = {**item.data, 'id': item.id}
            resolved_filename = format_template(resolved_filename, format_data)

        log_file = resolved_dir / resolved_filename
        save_messages(log_file, item.data["messages"], item.data["response"].content)

    return save_item_chat_action
