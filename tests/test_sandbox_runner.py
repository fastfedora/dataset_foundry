"""
Tests for the sandbox manager functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from dataset_foundry.utils.docker.sandbox_runner import SandboxRunner, SandboxConfig, SandboxResult
from dataset_foundry.utils.docker.container_manager import ContainerConfig, ContainerResult
from dataset_foundry.types.unit_test_result import UnitTestResult


class TestSandboxConfig:
    """Test SandboxConfig class."""

    def test_sandbox_config_creation(self):
        """Test creating a SandboxConfig instance."""
        container_config = ContainerConfig(
            image="test-image:latest",
            command=["python"]
        )

        config = SandboxConfig(
            container=container_config
        )

        assert config.container.image == "test-image:latest"
        assert config.container.command == ["python"]


class TestSandboxRunner:
    """Test SandboxRunner class."""

    def test_sandbox_runner_initialization(self):
        """Test SandboxRunner initialization."""
        container_manager = Mock()
        sandbox_runner = SandboxRunner("test-sandbox", container_manager)

        assert sandbox_runner.container_manager == container_manager
        assert sandbox_runner.runner_name == "test-sandbox"

    @pytest.mark.asyncio
    async def test_run_tests_in_sandbox(self, tmp_path):
        """Test running tests in sandbox."""
        # Create test files
        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
import pytest

def test_example():
    assert True
""")

        source_file = tmp_path / "example.py"
        source_file.write_text("""
def example_function():
    return True
""")

        # Mock container manager
        container_manager = Mock()
        container_manager.image_exists.return_value = True

        # Mock container result
        mock_result = ContainerResult(
            exit_code=0,
            stdout="1 passed",
            stderr="",
            logs="",
            container_id="test-container-id"
        )

        container_manager.run_container = AsyncMock(return_value=mock_result)

        # Create sandbox runner
        sandbox_runner = SandboxRunner("test-sandbox", container_manager)

        # Mock the config loading
        with patch.object(sandbox_runner, '_load_config'):
            sandbox_runner._config = SandboxConfig(
            container=ContainerConfig(
                image="test-image:latest",
                command=["python"]
            )
        )

        # Mock the image building
        with patch.object(sandbox_runner, '_ensure_image_built'):
        # Run tests
        result = await sandbox_runner.run(
            target_file=test_file,
            workspace_dir=tmp_path,
            command=["python", "-m", "pytest", "-v", test_file.name],
            timeout=300,
            stream_logs=False
        )

        # Verify result
        assert isinstance(result, SandboxResult)
        assert result.exit_code == 0
        assert result.stdout == "1 passed"
        assert result.stderr == ""
        assert result.container_id == "test-container-id"

    def test_create_container_config(self):
        """Test container configuration creation."""
        container_manager = Mock()
        sandbox_runner = SandboxRunner("test-sandbox", container_manager)

        # Mock the config
        sandbox_runner._config = SandboxConfig(
            container=ContainerConfig(
                image="test-image:latest",
                environment={"TEST_VAR": "test_value"},
                command=["python"]
            )
        )

        workspace_path = Path("/tmp/workspace")
        test_file = Path("/tmp/test.py")
        command = ["python", test_file.name]

        config = sandbox_runner._create_container_config(
            workspace_path,
            test_file,
            command
        )

        assert config.image == "test-image:latest"
        assert config.command == command
        assert config.environment == {"TEST_VAR": "test_value"}

    def test_create_container_config_no_command(self):
        """Test container configuration creation with no command."""
        container_manager = Mock()
        sandbox_runner = SandboxRunner("test-sandbox", container_manager)

        workspace_path = Path("/tmp/workspace")
        test_file = Path("/tmp/test.py")

        with pytest.raises(ValueError, match="No command provided for sandbox"):
            sandbox_runner._create_container_config(
                workspace_path,
                test_file,
                None
            )


class TestSandboxResult:
    """Test SandboxResult class."""

    def test_sandbox_result_creation(self):
        """Test creating a SandboxResult instance."""
        result = SandboxResult(
            exit_code=0,
            stdout="test output",
            stderr="test error",
            logs="test logs",
            container_id="test-container-id"
        )

        assert result.exit_code == 0
        assert result.stdout == "test output"
        assert result.stderr == "test error"
        assert result.logs == "test logs"
        assert result.container_id == "test-container-id"