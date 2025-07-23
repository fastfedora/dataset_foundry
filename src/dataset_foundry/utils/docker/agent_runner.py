"""
Agent runner for executing different types of agents in containers.
"""

import logging
import json
import yaml
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional, List

from docker.types import Mount
from pydantic import BaseModel

from .container_manager import BuildConfig, ContainerManager, ContainerConfig, ContainerResult
from ..params.resolve_environment_dict import resolve_environment_dict

logger = logging.getLogger(__name__)
agent_configs_dir = Path(__file__).parent.parent.parent / "configs" / "agents"


class AgentLogsConfig(BaseModel):
    """Configuration for agent logs."""
    format: Optional[str] = None


class AgentConfig(BaseModel):
    """Configuration for an agent type."""
    name: str
    container: ContainerConfig
    logs: Optional[AgentLogsConfig] = None


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


class AgentRunner:
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
                container_config,
                timeout=timeout,
                stream_logs=stream_logs,
                logs_format=self._config.logs.format
            )

            result = self._process_container_result(container_result, inputs, output_dir)

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
                name=self.agent_type,
                container=ContainerConfig(**config_data['container']),
                logs=AgentLogsConfig(**config_data.get('logs', {})),
            )
        else:
            raise ValueError(
                f"Unknown agent type: {self.agent_type}: "
                f"No agent configuration found at {agent_config_path}"
            )

    async def _ensure_image_built(self, stream_logs: bool = False):
        """Ensure the agent's Docker image is built."""

        config = deepcopy(self._config.container.build or BuildConfig())
        agent_config_dir = agent_configs_dir / self._config.name

        if not config.context:
            config.context = agent_config_dir
        elif not Path(config.context).is_absolute():
            config.context = agent_config_dir / config.context

        config.args = resolve_environment_dict(config.args)
        build_required = self._image_build_required(config) # requires resolved `config`

        # `build_required` can only be false if the image exists
        if not build_required:
            logger.info(f"Image {self._config.container.image} already exists")
            return

        if config.context and Path(config.context).exists():
            await self.container_manager.build_image(
                image_name=self._config.container.image,
                config=config,
                stream_logs=stream_logs
            )
        else:
            raise ValueError(f"No context found for agent {self._config.name} at {config.context}")

    def _image_build_required(self, build_config: BuildConfig) -> bool:
        try:
            image_name = self._config.container.image
            last_built = self.container_manager.get_image_last_built(image_name)

            if last_built is None:
                return True

            dockerfile_mtime = self._get_dockerfile_last_modified(build_config)

            if not dockerfile_mtime or dockerfile_mtime > last_built:
                return True

            # TODO: If agents.yaml has `build` section that has been modified since last build,
            #       then also we need to rebuild the image. [fastfedora 22.Jul.25]

            return False
        except Exception as e:
            return True

    def _get_dockerfile_last_modified(self, build_config: BuildConfig) -> Optional[float]:
        """Get the last modified time of the Dockerfile."""
        dockerfile_path = build_config.dockerfile or "Dockerfile"

        if not Path(dockerfile_path).exists():
            dockerfile_path = build_config.context / dockerfile_path

        dockerfile = Path(dockerfile_path)

        return dockerfile.stat().st_mtime if dockerfile.exists() else None

    def _prepare_container_config(
        self,
        inputs: AgentInputs,
        output_dir: Path
    ) -> ContainerConfig:
        """Prepare container configuration for agent execution."""

        config = deepcopy(self._config.container)
        image_config = self.container_manager.get_image_config(self._config.container.image)
        working_dir = config.working_dir or image_config.get("WorkingDir")

        if not working_dir:
            raise ValueError(f"No working directory configured for {self.agent_type}")

        inputs_dir = Path(working_dir) / "input"

        if not config.volumes:
            config.volumes = []
        else:
            for volume in config.volumes:
                if not Path(volume['Source']).is_absolute():
                    volume['Source'] = str(output_dir / volume['Source'])

        config.volumes.extend([
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

        if not config.environment:
            config.environment = {}

        config.environment.update({
            "ITEM_ID": inputs.item_id,
            "OUTPUT_DIR": f"{working_dir}/output",
            "CONTEXT_DATA": json.dumps(inputs.context_data),
            "PROMPT": inputs.prompt,
        })

        config.environment = resolve_environment_dict(config.environment)

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
            "agent_type": self.agent_type,
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
        )