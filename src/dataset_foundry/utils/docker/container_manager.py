"""
Container manager for orchestrating Docker containers.
"""

import asyncio
import logging
import datason.json as json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import docker
from docker.errors import DockerException
from docker.types import Mount
from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)

# Codes returned from `timeout` command indicating a timeout occurred
EXIT_CODE_TIMEOUT = 124
EXIT_CODE_SIGKILL = 137

# Buffer time in seconds to add to the container timeout to allow the `timeout` command to execute
TIMEOUT_BUFFER = 10

class BuildConfig(BaseModel):
    """Configuration for building a Docker image."""

    context: Optional[str] = None
    """Either a path to a directory containing a Dockerfile, or a URL to a Git repository."""

    dockerfile: Optional[str] = None
    """The path to an alternate Dockerfile to build."""

    target: Optional[str] = None
    """The stage to build as defined inside a multi-stage Dockerfile."""

    args: Optional[Dict[str, str]] = None
    """The build arguments to pass to the Dockerfile."""


class ContainerConfig(BaseModel):
    """Configuration for a Docker container."""

    model_config = { "arbitrary_types_allowed": True }

    image: str
    """The image to run."""

    build: Optional[BuildConfig] = None
    """The settings to use when building the image."""

    command: Optional[List[str]] = None
    """The command to run in the container."""

    entrypoint: Optional[List[str]] = None
    """The entrypoint for the container, overriding the default entrypoint."""

    user: Optional[str] = None
    """The user to run commands as inside the container."""

    working_dir: Optional[str] = None
    """The working directory for the container."""

    environment: Optional[Dict[str, str]] = None
    """The environment variables to set in the container."""

    network_mode: Optional[str] = None
    """The network mode for the container."""

    volumes: Optional[Union[List[str], List[Mount]]] = None
    """The volumes to mount in the container."""

    cap_add: Optional[List[str]] = None
    """The capabilities to add to the container."""

    cap_drop: Optional[List[str]] = None
    """The capabilities to drop from the container."""

    auto_remove: Optional[bool] = True
    """Whether to remove the container when it has finished running. Default: True."""

    timeout: Optional[int] = 3600
    """The timeout for the container to run."""

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the container configuration."""
        if "build" in values:
            values["build"] = BuildConfig(**values["build"])

        if "volumes" in values and values["volumes"] is not None:
            values["volumes"] = [cls.parse_mount(volume) for volume in values["volumes"]]

        return values

    @classmethod
    def parse_mount(cls, config: Union[str, Dict[str, Any], Mount]) -> Mount:
        """Parse a mount configuration into a Mount object."""
        if isinstance(config, Mount):
            return config

        elif isinstance(config, str):
            # Parse Docker Compose shorthand: 'host_path:container_path[:mode]'
            parts = config.split(":")
            if len(parts) < 2:
                raise ValueError(f"Invalid volume format: {config}")

            source = parts[0]
            target = parts[1]
            mode = parts[2] if len(parts) > 2 else None

            if source == "tmpfs":
                mount_type = "tmpfs"
            elif source.startswith(".") or Path(source).is_absolute():
                mount_type = "bind"
            else:
                mount_type = "volume"

            return Mount(source=source, target=target, read_only=(mode == 'ro'), type=mount_type)

        elif isinstance(config, dict):
            # Long syntax: already a dictionary, convert to Mount
            return Mount(**config)


class ContainerResult(BaseModel):
    """Result from container execution."""
    exit_code: int
    stdout: str
    stderr: str
    logs: str
    container_id: str


class ContainerManager:
    """Manages Docker container lifecycle and execution."""

    _docker_client: docker.DockerClient

    def __init__(self, docker_client: Optional[docker.DockerClient] = None):
        """
        Initialize the container manager.

        Args:
            docker_client: Optional Docker client instance
        """
        try:
            self._docker_client = docker_client or docker.from_env()
        except Exception as e:
            error = str(e)

            # HACK: The docker library should be throwing a more specific error here, but it's not
            #       so we're checking for the error message manually. [fastfedora 21.Jul.25]
            if (
                "while fetching server API version" in error and
                "Connection aborted" in error and
                "FileNotFoundError" in error
            ):
                raise DockerException("Docker does not appear to be running") from None
            else:
                raise e

    def image_exists(self, image_name: str) -> bool:
        """Returns True if a Docker image exists with no errors; False otherwise."""
        try:
            self._docker_client.images.get(image_name)

            # If no exception is raised, the image exists
            return True
        except:
            return False

    def get_image_last_built(self, image_name: str) -> Optional[float]:
        """Get the configuration of a Docker image."""
        try:
            created = self._docker_client.images.get(image_name).attrs['Created']
            metadata = self._docker_client.images.get(image_name).attrs['Metadata']
            last_tag_time = metadata['LastTagTime'] if metadata else None
            last_built = last_tag_time or created

            return datetime.fromisoformat(last_built.replace('Z', '+00:00')).timestamp()
        except Exception as e:
            return None

    def get_image_config(self, image_name: str) -> Any:
        """Get the configuration of a Docker image."""
        return self._docker_client.images.get(image_name).attrs['Config']

    async def build_image(
        self,
        image_name: str,
        config: BuildConfig,
        stream_logs: bool = False
    ) -> str:
        """
        Build a Docker image from a Dockerfile.

        Args:
            image_name: Name for the built image
            config: Configuration settings for building the image
            stream_logs: Whether to stream build logs to logger.info (default: False)

        Returns:
            Image ID of the built image
        """
        try:
            if not config.context:
                raise ValueError("The 'context' path is required for building an image")

            logger.info(f"Building image {image_name} from {config.context}")

            # Use low-level API for streaming logs
            response = self._docker_client.api.build(
                path=str(config.context),
                dockerfile=config.dockerfile,
                buildargs=config.args,
                target=config.target,
                tag=image_name,
                rm=True,
                decode=True
            )

            # Stream logs to logger
            image_id = None
            for chunk in response:
                if 'stream' in chunk:
                    log_line = chunk['stream'].strip()
                    if stream_logs:
                        logger.info(f"[Docker Build] {log_line}")
                elif 'error' in chunk:
                    error_msg = chunk['error'].strip()
                    if error_msg:
                        raise DockerException(error_msg)
                elif 'aux' in chunk:
                    # Extract image ID from aux data
                    image_id = chunk['aux'].get('ID')

            if not image_id:
                raise DockerException("Failed to build image - no image ID returned")

            logger.info(f"Successfully built image {image_name}: {image_id}")

            return image_id

        except DockerException as e:
            logger.error(f"Error building image {image_name}: {e}")
            raise

    async def run_container(
        self,
        config: ContainerConfig,
        timeout: Optional[int] = None,
        stream_logs: bool = False,
        logs_format: Optional[str] = None
    ) -> ContainerResult:
        """
        Run a container with the given configuration.

        Args:
            config: Container configuration
            timeout: Optional timeout in seconds
            stream_logs: Whether to stream container logs to logger.info (default: False)
            logs_format: Format of the logs to stream (default: None)
        Returns:
            ContainerResult with execution details
        """
        container = None
        timeout = timeout or config.timeout

        try:
            logger.debug(f"Running container {config.image} with command {config.command}")

            container = self._docker_client.containers.run(
                image=config.image,
                command=["timeout", f"{timeout}s"] + config.command,
                entrypoint=config.entrypoint,
                user=config.user,
                environment=config.environment,
                mounts=config.volumes,
                working_dir=config.working_dir,
                network_mode=config.network_mode,
                cap_add=config.cap_add,
                cap_drop=config.cap_drop,
                detach=True,
                # NOTE: Handling remove manually in finally block; otherwise if the command executes
                #       too quickly, the container will be removed before we have a chance to grab
                #       the logs in `_wait_for_container`. [fastfedora 22.Jul.25]
                # auto_remove=config.auto_remove,
            )

            # NOTE: We add a buffer to the timeout to allow the `timeout` command to execute
            #       before the container is killed. [fastfedora 5.Aug.25]
            return await self._wait_for_container(
                container,
                timeout + TIMEOUT_BUFFER,
                stream_logs,
                logs_format
            )
        except DockerException as e:
            logger.error(f"Docker error: {e}")
            raise
        except Exception as e:
            logger.error(f"Container execution error: {e}")
            raise
        finally:
            if container:
                if config.auto_remove:
                    # Remove the container and its volumes
                    container.remove(v=True)
                else:
                    # Handle orphaned containers: only if auto_remove=False & container still exists
                    try:
                        # Check if container still exists (hasn't been auto-removed)
                        container.reload()
                        logger.info(f"Container {container.id} completed successfully")
                    except Exception:
                        # Container was already removed or doesn't exist
                        pass

    async def _wait_for_container(
        self,
        container,
        timeout: int,
        stream_logs: bool,
        logs_format: Optional[str] = None
    ) -> ContainerResult:
        """Wait for a detached container to complete while streaming logs."""
        logs_task = None
        stdout_task = None
        stderr_task = None

        try:
            # Collect each stream in a separate buffer, plus an interweaved buffer for full logs
            logs = []
            stdout = []
            stderr = []
            logs_stream = container.logs(stdout=True, stderr=True, stream=True, follow=True)
            stdout_stream = container.logs(stdout=True, stderr=False, stream=True, follow=True)
            stderr_stream = container.logs(stdout=False, stderr=True, stream=True, follow=True)

            # Only print the interweaved logs; the other streams are just for collection
            logs_task = asyncio.create_task(
                self._stream_container_logs(logs_stream, logs, container.id, stream_logs, logs_format)
            )
            stdout_task = asyncio.create_task(
                self._stream_container_logs(stdout_stream, stdout, container.id, False, logs_format)
            )
            stderr_task = asyncio.create_task(
                self._stream_container_logs(stderr_stream, stderr, container.id, False, logs_format)
            )

            exit_code = await self._wait_for_container_completion(container, timeout)

            # Detect if timeout occurred
            if exit_code == EXIT_CODE_TIMEOUT or exit_code == EXIT_CODE_SIGKILL:
                if exit_code == EXIT_CODE_TIMEOUT:
                    message = f"Process timed out and shutdown gracefully"
                else:
                    message = f"Process timed out and was killed by the system"

                logger.warning(f"{message} in container {container.id} (exit code: {exit_code})")
                stderr.append(f"WARNING: {message}")
                logs.append(f"WARNING: {message}")

            return ContainerResult(
                exit_code=exit_code,
                stdout='\n'.join(stdout),
                stderr='\n'.join(stderr),
                logs='\n'.join(logs),
                container_id=container.id
            )

        except Exception as e:
            logger.error(f"Error waiting for container {container.id}: {e}")
            raise
        finally:
            # Always clean up log tasks, even if there was an exception or timeout
            if logs_task:
                await self._cleanup_log_task(logs_task)
            if stdout_task:
                await self._cleanup_log_task(stdout_task)
            if stderr_task:
                await self._cleanup_log_task(stderr_task)

    async def _stream_container_logs(
        self,
        log_stream,
        logs_buffer: list,
        container_id: str,
        stream_logs: bool,
        logs_format: Optional[str] = None
    ):
        """Stream logs from container in real-time."""
        try:
            for log_chunk in log_stream:
                log_line = log_chunk.decode('utf-8', errors='ignore').strip()
                logs_buffer.append(log_line)
                if stream_logs:
                    if logs_format == "json":
                        try:
                            log_line = self._format_json_log(log_line)
                        except:
                            pass

                    logger.info(f"[Container {container_id[:12]}] {log_line}")
        except Exception as e:
            logger.warning(f"Error streaming logs: {e}")

    def _format_json_log(self, log_line: str) -> str:
        """Format a JSON log line."""
        log_data = json.loads(log_line)
        log_line = json.dumps(log_data, indent=2)
        log_line = log_line.replace("\\n", "\n")

        return log_line

    async def _wait_for_container_completion(self, container, timeout: int) -> int:
        """Wait for container to complete and return exit code."""
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(container.wait),
                timeout=timeout
            )
            return result.get('StatusCode', 0)
        except asyncio.TimeoutError:
            logger.warning(f"Container {container.id} timed out after {timeout} seconds")
            # Stop the container if it timed out
            container.stop(timeout=10)
            return -1

    async def _cleanup_log_task(self, log_task: asyncio.Task):
        """Clean up the log streaming task."""
        log_task.cancel()
        try:
            await log_task
        except asyncio.CancelledError:
            pass
