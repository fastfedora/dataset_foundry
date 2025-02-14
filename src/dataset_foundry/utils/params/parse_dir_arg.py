from pathlib import Path

def parse_dir_arg(value: str, defaultValue: Path, create: bool = False) -> Path:
    """
    Parse an argument pointing to a directory into a Path object, optionally creating the directory
    if it doesn't exist.

    Args:
        value (str): The value to parse.
        defaultValue (Path): The default value to return if the value is None.
        create (bool): Whether to create the directory if it doesn't exist.
    """
    path = Path(value) if value else defaultValue

    if create and not path.exists():
        path.mkdir(parents=True, exist_ok=create)

    return path
