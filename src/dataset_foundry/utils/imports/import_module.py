from importlib.util import spec_from_file_location, module_from_spec
import pathlib

from .enable_local_imports import enable_local_imports

def import_module(module_path):
    """
    Dynamically imports all exports from a given Python module file.

    Args:
        module_path (str): The path to the Python module file to import.

    Returns:
        module: The imported module.
    """
    module_path = pathlib.Path(module_path)

    if not module_path.exists():
        raise FileNotFoundError(f"Module {module_path} not found.")

    enable_local_imports()

    module_name = module_path.stem
    spec = spec_from_file_location(module_name, module_path)

    if spec is None:
        raise FileNotFoundError(f"Module {module_path} not found.")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
