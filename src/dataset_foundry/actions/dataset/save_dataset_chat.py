from typing import Callable, Optional, Union

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value
from ...utils.save_messages import save_messages
from ...utils.format.format_template import format_template

def save_dataset_chat(
        dir: Union[Callable,Key,str] = Key("context.log_dir"),
        filename: Union[Callable,Key,str] = "log.yaml",
        chat_key: Union[Callable,Key,str] = "chat",
    ) -> DatasetAction:
    async def save_dataset_chat_action(dataset: Dataset, context: Context):
        resolved_dir = resolve_dataset_value(dir, dataset, context, required_as="dir")
        resolved_filename = resolve_dataset_value(filename, dataset, context, required_as="filename")
        resolved_chat_key = resolve_dataset_value(chat_key, dataset, context, required_as="chat_key")

        log_file = resolved_dir / resolved_filename
        chat = dataset.metadata[resolved_chat_key]

        save_messages(log_file, chat["messages"], chat["response"].content)

    return save_dataset_chat_action
