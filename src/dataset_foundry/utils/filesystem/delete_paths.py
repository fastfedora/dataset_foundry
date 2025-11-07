import logging
import os
from pathlib import Path
from typing import List, Optional

from .find_paths import find_paths

logger = logging.getLogger(__name__)


def delete_paths(
    dir: str | Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> dict:
    """
    Delete files and directories from a directory based on include and exclude patterns.

    Args:
        dir: Directory to delete files from
        include: List of glob patterns to include
        exclude: List of glob patterns to exclude

    Returns:
        Dictionary containing the deleted files and directories and any errors that occurred
    """
    result = {
        "deleted_dirs": [],
        "deleted_files": [],
        "errors": []
    }

    try:
        target_dir = Path(dir)
        if not target_dir.exists():
            result["errors"].append("Directory does not exist")
            return result

        matching_paths = find_paths(dir, include=include, exclude=exclude, topdown=False)
        dirs_to_delete = {path for path, path_type in matching_paths if path_type == 'directory'}

        for relative_path, path_type in matching_paths:
            is_inside_deleted_dir = any(
                relative_path.startswith(deleted_dir + "/") for deleted_dir in dirs_to_delete
            )

            if path_type == 'file':
                try:
                    os.remove(target_dir / relative_path)
                    if not is_inside_deleted_dir:
                        result["deleted_files"].append(relative_path)
                except OSError as e:
                    result["errors"].append(f"Failed to delete file {relative_path}: {e}")
            else:  # directory
                try:
                    os.rmdir(target_dir / relative_path)
                    if not is_inside_deleted_dir:
                        result["deleted_dirs"].append(relative_path)
                except OSError as e:
                    result["errors"].append(f"Failed to delete directory {relative_path}: {e}")

    except Exception as e:
        result["errors"].append(f"Error during cleaning: {e}")

    return result
