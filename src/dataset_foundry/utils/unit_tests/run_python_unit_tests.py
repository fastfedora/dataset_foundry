import logging
import os
from pathlib import Path
import re
from subprocess import CompletedProcess, CalledProcessError, run
import sys
from typing import Union

from dataset_foundry.types.unit_test_result import UnitTestResult

logger = logging.getLogger(__name__)

def parse_pytest_results(result: Union[CompletedProcess, CalledProcessError]) -> UnitTestResult:
    passed_match = re.search(r'(\d+)\s*passed', result.stdout)
    failed_match = re.search(r'(\d+)\s*failed', result.stdout)
    num_passed = int(passed_match.group(1)) if passed_match else 0
    num_failed = int(failed_match.group(1)) if failed_match else 0

    return UnitTestResult(
        command=result.args or result.cmd,
        num_passed=num_passed,
        num_failed=num_failed,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr
    )

def run_python_unit_tests(test_path: Path) -> UnitTestResult:
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

    logger.debug(f"Running unit tests for {test_path.name}")

    try:
        result = parse_pytest_results(run(
            [str(pytest_path), test_path, "-v"],
            check=True,
            capture_output=True,
            text=True
        ))
    except CalledProcessError as e:
        result = parse_pytest_results(e)

    logger.debug(f"Unit test results: {result}")

    return result
