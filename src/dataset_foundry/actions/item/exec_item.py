import logging
from typing import Callable, Optional, Union
import subprocess
import asyncio
from pathlib import Path

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

logger = logging.getLogger(__name__)

def exec_item(
        command: Union[Callable, Key, str],
        cwd: Optional[Union[Callable, Key, str]] = Key("context.output_dir"),
        output_key: Union[Callable, Key, str] = "exec_result",
        timeout: Union[Callable,Key,int] = 10,
    ) -> ItemAction:
    """
    Runs a shell command in the specified working directory and stores the result in the item.

    Args:
        command: The shell command to run (string or callable/key).
        cwd: The working directory to run the command in (string or callable/key).
        output_key: The key to store the result under in the item (default: 'exec_result').
        timeout: The timeout for the command in seconds (default: 10).
    """
    async def exec_item_action(item: DatasetItem, context: Context):
        resolved_command = resolve_item_value(command, item, context, required_as="command")
        resolved_cwd = resolve_item_value(cwd, item, context, required_as="cwd")
        resolved_output_key = resolve_item_value(output_key, item, context)
        resolved_timeout = resolve_item_value(timeout, item, context)

        if isinstance(resolved_cwd, str):
            resolved_cwd = Path(resolved_cwd)

        logger.info(f"Running command: {resolved_command} (cwd={resolved_cwd})")

        def run_command():
            try:
                result = subprocess.run(
                    resolved_command,
                    shell=True,
                    cwd=resolved_cwd,
                    capture_output=True,
                    text=True,
                    timeout=resolved_timeout,
                )
                return {
                    "command": resolved_command,
                    "cwd": str(resolved_cwd),
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            except Exception as e:
                return {
                    "command": resolved_command,
                    "cwd": str(resolved_cwd),
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                }

        exec_result = await asyncio.to_thread(run_command)

        item.push({ resolved_output_key: exec_result }, exec_item)

    return exec_item_action