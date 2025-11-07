import logging
from pathlib import Path
from typing import Callable, List, Union

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value

logger = logging.getLogger(__name__)


def load_gitignore(
    path: Union[Callable, Key, str],
    output_key: Union[Callable, Key, str] = "gitignore",
) -> ItemAction:
    """
    Creates an action that loads and parses a .gitignore file, saving the patterns to the item.

    Args:
        path: Path to the .gitignore file
        output_key: Key to store the parsed patterns in the item

    Returns:
        ItemAction that loads and parses the gitignore file
    """
    async def load_gitignore_action(item: DatasetItem, context: Context):
        resolved_path = resolve_item_value(path, item, context, required_as="path")
        resolved_output_key = resolve_item_value(output_key, item, context)

        gitignore_path = Path(resolved_path) / ".gitignore"

        if not gitignore_path.exists():
            logger.warning(f".gitignore file at {gitignore_path} does not exist")
            result = {
                "patterns": [],
                "errors": [".gitignore file does not exist"]
            }
            item.push({resolved_output_key: result}, load_gitignore)
            return

        if not gitignore_path.is_file():
            logger.warning(f"Path {gitignore_path} is not a file")
            result = {
                "patterns": [],
                "errors": ["Path is not a file"]
            }
            item.push({resolved_output_key: result}, load_gitignore)
            return

        patterns = _parse_gitignore(gitignore_path)

        result = {
            "patterns": patterns,
            "errors": []
        }

        item.push({ resolved_output_key: result }, load_gitignore)

    return load_gitignore_action


def _parse_gitignore(gitignore_path: Path) -> List[str]:
    """
    Parse a .gitignore file and return list of patterns.

    Args:
        gitignore_path: Path to the .gitignore file

    Returns:
        List of glob patterns from the gitignore file
    """
    patterns = []

    try:
        with open(gitignore_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)

    except Exception as e:
        logger.error(f"Failed to parse gitignore file {gitignore_path}: {e}")

    return patterns
