from pydantic import BaseModel
from typing import Any, List

class UnitTestResult(BaseModel):
    command: List[Any]
    num_passed: int
    num_failed: int
    returncode: int
    stdout: str
    stderr: str

    @property
    def total_tests(self) -> int:
        return self.num_passed + self.num_failed

    @property
    def success(self) -> bool:
        return self.num_failed == 0

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        passed = f"{self.num_passed} passed" if self.num_passed > 0 else ""
        failed = f"{self.num_failed} failed" if self.num_failed > 0 else ""
        stderr = f", stderr: {self.stderr}" if self.stderr else ""
        error = f"(code: {self.returncode}{stderr})" if not self.success else ""

        if passed and failed:
            passed += ","

        return f"{status}: {self.total_tests} tests - {passed} {failed} {error}"
