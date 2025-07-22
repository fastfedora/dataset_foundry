"""
Agent runner for executing different types of agents in containers.
"""

import logging
import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from .container_manager import ContainerManager, ContainerConfig, ContainerResult

logger = logging.getLogger(__name__)
agent_configs_dir = Path(__file__).parent.parent.parent / "configs" / "agents"


class AgentConfig(BaseModel):
    """Configuration for an agent type."""
    name: str
    image: str
    entrypoint: Optional[List[str]] = None
    working_dir: str = "/workspace"
    environment: Optional[Dict[str, str]] = None
    volumes: Optional[Dict[str, Dict[str, str]]] = None
    build_args: Optional[Dict[str, str]] = None


class AgentInputs(BaseModel):
    """Input files for agent execution."""
    instructions_file: str
    prompt_file: str
    spec_file: str
    output_dir: str
    item_id: str
    context_data: Dict[str, Any]
    repo_path: Optional[str] = None


class AgentResult(BaseModel):
    """Result from agent execution."""
    success: bool
    exit_code: int
    output_files: List[str]
    logs: str
    metadata: Dict[str, Any]


class AgentRunner:
    """Runs different types of agents in Docker containers."""

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
        self.agent_type = agent_type
        self.container_manager = container_manager or ContainerManager()
        self._config: Optional[AgentConfig] = None

    async def run_agent(
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

            logger.info(f"Running agent {self.agent_type} (attempt {attempt})")
            container_result = await self.container_manager.run_container(
                container_config, timeout=timeout, stream_logs=stream_logs
            )

            result = self._process_container_result(container_result, output_dir, inputs.item_id)

            logger.info(f"Agent {self.agent_type} completed with exit code {result.exit_code}")
            return result

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    async def _load_config(self) -> AgentConfig:
        """Load agent-specific configuration from configs/agents/{agent_name}/agent.yml."""
        agent_config_path = agent_configs_dir / self.agent_type / "agent.yml"

        if agent_config_path.exists():
            with open(agent_config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            logger.info(f"Loaded agent configuration from {agent_config_path}")

            return AgentConfig(
                **config_data,
                name=self.agent_type,
            )
        else:
            raise ValueError(
                f"Unknown agent type: {self.agent_type}: "
                f"No agent configuration found at {agent_config_path}"
            )

    async def _ensure_image_built(self, stream_logs: bool = False):
        """Ensure the agent's Docker image is built."""
        if self.container_manager.image_exists(self._config.container.image):
            logger.info(f"Image {self._config.container.image} already exists")
            return

        dockerfile_path = agent_configs_dir / self._config.name
        if dockerfile_path and dockerfile_path.exists():
            await self.container_manager.build_image(
                dockerfile_path=dockerfile_path,
                image_name=self._config.image,
                build_args=self._config.build_args,
                stream_logs=stream_logs
            )
        else:
            raise ValueError(f"No Dockerfile found for agent {self._config.name}")

    def _prepare_container_config(
        self,
        inputs: AgentInputs,
        output_dir: Path
    ) -> ContainerConfig:
        """Prepare container configuration for agent execution."""

        volumes = {
            str(output_dir): {"bind": "/workspace", "mode": "rw"},
            inputs.instructions_file: {"bind": "/workspace/AGENTS.md", "mode": "ro"},
            inputs.prompt_file: {"bind": "/workspace/PROMPT.md", "mode": "ro"},
            inputs.spec_file: {"bind": "/workspace/spec.yaml", "mode": "ro"},
        }

        # Add agent-specific volumes
        if self._config.volumes:
            volumes.update(self._config.volumes)

        environment = {
            "ITEM_ID": inputs.item_id,
            "OUTPUT_DIR": "/workspace/repo",
            "CONTEXT_DATA": json.dumps(inputs.context_data),
        }

        if self._config.environment:
            # Handle environment variable substitution
            for key, value in self._config.environment.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    # Extract variable name and get from system environment
                    var_name = value[2:-1]  # Remove ${ and }
                    system_value = os.environ.get(var_name)
                    if system_value:
                        environment[key] = system_value
                    else:
                        logger.warning(f"Environment variable {var_name} not found")
                else:
                    environment[key] = value

        command = self._config.entrypoint or [
            "python", "-m", "agent.main",
            "--instructions", "/workspace/AGENTS.md",
            "--prompt", "/workspace/PROMPT.md",
            "--spec", "/workspace/spec.yaml",
            "--repo-dir", "/workspace/repo"
        ]

        return ContainerConfig(
            image=self._config.image,
            command=command,
            environment=environment,
            volumes=volumes,
            working_dir=self._config.working_dir,
            remove=True,
            timeout=3600
        )

    def _process_container_result(
        self,
        container_result: ContainerResult,
        output_dir: Path,
        item_id: str
    ) -> AgentResult:
        """Process container execution result."""

        repo_dir = output_dir / "repo"
        repo_files = []
        if repo_dir.exists():
            for file_path in repo_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    repo_files.append(str(file_path.relative_to(repo_dir)))

        metadata = {
            "container_id": container_result.container_id,
            "exit_code": container_result.exit_code,
            "output_files": repo_files,
            "item_id": item_id,
            "agent_type": self.agent_type,
        }

        return AgentResult(
            success=container_result.exit_code == 0,
            exit_code=container_result.exit_code,
            output_files=repo_files,
            logs=container_result.logs,
            metadata=metadata
        )