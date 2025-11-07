import logging
from pathlib import Path
from typing import Callable, List, Optional, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.filesystem.delete_paths import delete_paths

logger = logging.getLogger(__name__)


def delete_files(
    dir: Union[Callable, Key, str],
    include: Optional[Union[Callable, Key, List[str]]] = None,
    exclude: Optional[Union[Callable, Key, List[str]]] = None,
    output_key: Union[Callable, Key, str] = "delete_files_result",
) -> ItemAction:
    """
    Creates an action that deletes files and directories based on the given patterns.

    Args:
        dir: Directory to delete files from
        include: List of glob patterns to match files for deletion
        exclude: List of glob patterns to exclude from deletion
        output_key: Key to store the deletion results in the item

    Returns:
        ItemAction that deletes matching files and directories
    """
    async def delete_files_action(item: DatasetItem, context: Context):
        resolved_dir = resolve_item_value(dir, item, context, required_as="dir")
        resolved_include = resolve_item_value(include, item, context)
        resolved_exclude = resolve_item_value(exclude, item, context)
        resolved_output_key = resolve_item_value(output_key, item, context)

        target_dir = Path(resolved_dir)
        if not target_dir.exists():
            raise ValueError(f"Directory {target_dir} does not exist")
        if not target_dir.is_dir():
            raise ValueError(f"Path {target_dir} is not a directory")

        result = delete_paths(str(target_dir), include=resolved_include, exclude=resolved_exclude)
        result["deleted_paths"] = result["deleted_files"] + result["deleted_dirs"]

        item.push({ resolved_output_key: result }, delete_files)

        logger.info(f"Deleted {len(result['deleted_paths'])} items from {target_dir}")
        if result['errors']:
            logger.warning(f"Encountered {len(result['errors'])} errors during deletion")

    return delete_files_action
