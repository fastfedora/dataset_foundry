"""
Parse sandbox results into unit test results.
"""

import re
from pathlib import Path

from dataset_foundry.types.unit_test_result import UnitTestResult
from dataset_foundry.utils.docker.sandbox_runner import SandboxResult


def parse_python_unit_test_results(result: SandboxResult) -> UnitTestResult:
    """
    Parse a `SandboxResult` into a `UnitTestResult`.

    This function attempts to extract test results from the sandbox output, particularly looking for
    pytest-style output patterns.

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

    if passed_match or failed_match:
        # This looks like pytest output
        num_passed = int(passed_match.group(1)) if passed_match else 0
        num_failed = int(failed_match.group(1)) if failed_match else 0
    else:
        # Generic execution - treat as success/failure based on exit code
        num_passed = 1 if result.exit_code == 0 else 0
        num_failed = 1 if result.exit_code != 0 else 0

    return UnitTestResult(
        command=[f"docker run {result.container_id}"],
        num_passed=num_passed,
        num_failed=num_failed,
        returncode=result.exit_code,
        stdout=stdout,
        stderr=stderr
    )