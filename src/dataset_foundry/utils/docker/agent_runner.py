"""
Agent runner for executing different types of agents in containers.
"""

import datason.json as json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional, List

from docker.types import Mount
from pydantic import BaseModel

from .base_runner import BaseRunner, RunnerConfig
from .container_manager import ContainerConfig, ContainerManager, ContainerResult

logger = logging.getLogger(__name__)


class AgentConfig(RunnerConfig):
    """Configuration for an agent runner."""


class AgentInputs(BaseModel):
    """Input files for agent execution."""
    prompt: str
    instructions_file: str
    spec_file: str
    output_dir: str
    item_id: str
    context_data: Dict[str, Any]
    repo_path: Optional[str] = None


class AgentResult(BaseModel):
    """Result from agent execution."""
    metadata: Dict[str, Any]
    inputs: Dict[str, Any]
    success: bool
    exit_code: int
    output_files: List[str]
    logs: str
    stdout: str
    stderr: str


class AgentRunner(BaseRunner):
    """Runs different types of agents in Docker containers."""

    _config: Optional[AgentConfig] = None

    def __init__(
        self,
        agent_type: str,
        container_manager: Optional[ContainerManager] = None
    ):
        """
        Initialize the agent runner.

        Args:
            agent_type: Type of agent to run
            container_manager: Optional container manager instance
        """
        super().__init__(agent_type, "agents", "agent.yml", container_manager)

    async def run(
        self,
        inputs: AgentInputs,
        output_dir: Path,
        timeout: int = 3600,
        attempt: int = 1,
        stream_logs: bool = False
    ) -> AgentResult:
        """
        Run an agent with the given inputs.

        Args:
            inputs: Agent input files and data
            output_dir: Directory for agent output
            timeout: Execution timeout in seconds
            attempt: Current attempt number
            stream_logs: Whether to stream container logs to logger.info (default: False)

        Returns:
            AgentResult with execution details
        """
        try:
            if self._config is None:
                self._config = await self._load_config()

            await self._ensure_image_built(stream_logs)

            container_config = self._prepare_container_config(inputs, output_dir)

            logger.info(f"Running agent {self.runner_name} (attempt {attempt})")
            container_result = await self.container_manager.run_container(
                container_config,
                timeout=timeout,
                stream_logs=stream_logs,
                logs_format=self._config.logs.format if self._config.logs else None
            )

            result = self._process_container_result(container_result, inputs, output_dir)

            logger.info(f"Agent {self.runner_name} completed with exit code {result.exit_code}")
            return result

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    def _prepare_container_config(
        self,
        inputs: AgentInputs,
        output_dir: Path
    ) -> ContainerConfig:
        """Prepare container configuration for agent execution."""

        config = deepcopy(self._config.container)
        working_dir = self._get_working_dir(config)
        inputs_dir = Path(working_dir) / "input"

        self._prepare_volumes_config(config, [
            Mount(target=working_dir, source=str(output_dir), type="bind", read_only=False),
            Mount(
                target=f"{inputs_dir}/AGENTS.md",
                source=str(inputs.instructions_file),
                type="bind",
                read_only=True
            ),
            Mount(
                target=f"{inputs_dir}/spec.yaml",
                source=str(inputs.spec_file),
                type="bind",
                read_only=True
            ),
        ])
        self._prepare_environment_config(config, {
            "ITEM_ID": inputs.item_id,
            "OUTPUT_DIR": f"{working_dir}/output",
            "CONTEXT_DATA": json.dumps(inputs.context_data),
            "PROMPT": inputs.prompt,
        })

        return config

    def _process_container_result(
        self,
        container_result: ContainerResult,
        inputs: AgentInputs,
        output_dir: Path,
    ) -> AgentResult:
        """Process container execution result."""

        repo_dir = output_dir / "repo"
        repo_files = []
        if repo_dir.exists():
            for file_path in repo_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    repo_files.append(str(file_path.relative_to(repo_dir)))

        metadata = {
            "agent_type": self.runner_name,
            "container_id": container_result.container_id,
            "repo_dir": str(repo_dir),
        }

        return AgentResult(
            metadata=metadata,
            inputs=inputs.model_dump(),
            success=container_result.exit_code == 0,
            exit_code=container_result.exit_code,
            output_files=repo_files,
            logs=container_result.logs,
            stdout=container_result.stdout,
            stderr=container_result.stderr,
        )