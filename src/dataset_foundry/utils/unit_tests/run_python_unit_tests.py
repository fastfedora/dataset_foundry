import logging
from pathlib import Path
import subprocess
import sys
import os

logger = logging.getLogger(__name__)

def run_python_unit_tests(test_path: str):
    """
    Run the unit tests using pytest.

    Args:
        test_path (str): The path to the Python module file to run the unit tests on.

    Returns:
        result: The result of the unit tests.
    """
    pytest_path = Path(sys.executable).parent / ('pytest' if os.name != 'nt' else 'pytest.exe')

    if not pytest_path.exists():
        raise EnvironmentError(
            "pytest not found in virtual environment. "
            "Please install it with: pip install pytest"
        )

    try:
        result = subprocess.run(
            [str(pytest_path), test_path, "-v"],
            check=True,
            capture_output=True,
            text=True
        )

        # TODO: Standardize the return value of this function. [fastfedora 14.Feb.25]
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed with exit code {e.returncode}")

        # TODO: Standardize the return value of this function. [fastfedora 14.Feb.25]
        return e
