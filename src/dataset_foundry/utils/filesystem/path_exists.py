from pathlib import Path

def path_exists(path: str) -> bool:
    """Check if a path exists, with wildcard support for filenames"""
    if '*' in path:
        pattern = Path(path).name
        parent = Path(path).parent

        return any(p.exists() for p in parent.glob(pattern))
    else:
        return Path(path).exists()
