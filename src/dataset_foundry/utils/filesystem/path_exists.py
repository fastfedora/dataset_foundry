from pathlib import Path

def path_exists(path: str) -> bool:
    """Check if a path exists"""
    return Path(path).exists()
