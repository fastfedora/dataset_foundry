"""
Parse sandbox results into unit test results.
"""

import re

from dataset_foundry.types.unit_test_result import UnitTestResult
from dataset_foundry.utils.docker.sandbox_runner import SandboxResult


def parse_python_unit_test_results(result: SandboxResult) -> UnitTestResult:
    """
    Parse a `SandboxResult` into a `UnitTestResult`.

    This function attempts to extract test results from the sandbox output, particularly looking for
    pytest-style output patterns. If the tests were never run or the results could not be parsed,
    num_passed and num_failed within the returned `UnitTestResult` will be 0.

    Args:
        result: The result from sandbox execution

    Returns:
        `UnitTestResult` with parsed test information
    """
    stdout = result.stdout
    stderr = result.stderr

    # Try to parse pytest output if it looks like test results
    passed_match = re.search(r'(\d+)\s*passed', stdout)
    failed_match = re.search(r'(\d+)\s*failed', stdout)
    num_passed = int(passed_match.group(1)) if passed_match else 0
    num_failed = int(failed_match.group(1)) if failed_match else 0

    # NOTE: If the tests were never run or the results could not be parsed, num_passed and
    #       num_failed will be 0. [fastfedora 29.Dec.25]
    return UnitTestResult(
        command=[f"docker run {result.container_id}"],
        num_passed=num_passed,
        num_failed=num_failed,
        returncode=result.exit_code,
        stdout=stdout,
        stderr=stderr
    )