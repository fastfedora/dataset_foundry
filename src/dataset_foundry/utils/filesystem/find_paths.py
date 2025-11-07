import logging
import os
from pathlib import Path
from typing import List, Optional

import gitmatch

logger = logging.getLogger(__name__)


def find_paths(
    dir: str | Path,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    topdown: bool = True,
) -> List[tuple[str, str]]:
    """
    Find all files and directories matching the given include patterns, excluding those that match
    the exclude patterns.

    Pattern matching behavior:
    - Patterns are matched against paths relative to the search directory
    - Leading slash patterns (e.g., `/src/*.py`) match only from the root of the search directory
    - Patterns without leading slash match anywhere in the directory tree
    - Recursive `**` patterns match zero or more directories (e.g., `**/file.py` matches `file.py`
      at root)
    - Negation patterns (starting with `!`) are supported

    Args:
        dir: Directory to search
        include: Optional list of .gitignore patterns to include
        exclude: Optional list of .gitignore patterns to exclude
        topdown: Whether to walk the directory top-down or bottom-up

    Returns:
        List of tuples in the form (relative_path, 'file' | 'directory')
    """
    matching_paths = []
    dir_path = Path(dir) if isinstance(dir, str) else dir

    if not dir_path.exists():
        raise ValueError(f"Directory {dir_path} does not exist")
    if not dir_path.is_dir():
        raise ValueError(f"Path {dir_path} is not a directory")

    include_matcher = gitmatch.compile(include) if include else None
    exclude_matcher = gitmatch.compile(exclude) if exclude else None

    for root, dirs, files in os.walk(dir_path, topdown=topdown):
        for name, is_dir in [(f, False) for f in files] + [(d, True) for d in dirs]:
            relative_path = os.path.relpath(os.path.join(root, name), dir_path)
            should_include_path = _should_include_path(
                relative_path,
                is_dir=is_dir,
                include_matcher=include_matcher,
                exclude_matcher=exclude_matcher,
            )
            if should_include_path:
                matching_paths.append((relative_path, 'directory' if is_dir else 'file'))

    return matching_paths


def _should_include_path(
    relative_path: str,
    is_dir: bool,
    include_matcher: Optional[gitmatch.Gitignore],
    exclude_matcher: Optional[gitmatch.Gitignore],
) -> bool:
    """
    Check if a path should be included based on include/exclude patterns.

    Args:
        relative_path: Relative path to check
        is_dir: Whether the path is a directory
        include_matcher: Compiled gitignore matcher for include patterns
        exclude_matcher: Compiled gitignore matcher for exclude patterns

    Returns:
        True if the path should be included, False otherwise
    """
    # Normalize path separators for gitmatch (use forward slashes)
    normalized_path = relative_path.replace(os.sep, '/')

    # Check include patterns
    if include_matcher:
        match_result = include_matcher.match(normalized_path, is_dir=is_dir)
        if not match_result or not bool(match_result):
            return False

    # Check exclude patterns
    if exclude_matcher:
        match_result = exclude_matcher.match(normalized_path, is_dir=is_dir)
        if match_result and bool(match_result):
            return False

    return True


