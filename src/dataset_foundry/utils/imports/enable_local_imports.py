import pathlib
import sys

def enable_local_imports():
    """Ensure the project root is in the `sys.path` so that local imports work."""
    script_dir = pathlib.Path(__file__).resolve().parent
    local_import_root = script_dir.parent.parent.parent

    if local_import_root not in sys.path:
        sys.path.insert(0, str(local_import_root))
