"""
Container manager for orchestrating Docker containers.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import docker
from docker.errors import DockerException
from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)


class ContainerConfig(BaseModel):
    """Configuration for a Docker container."""
    image: str
    command: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    volumes: Optional[Dict[str, Dict[str, str]]] = None
    working_dir: Optional[str] = None
    network_mode: Optional[str] = None
    remove: bool = True
    timeout: int = 3600


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

    async def build_image(
        self,
        dockerfile_path: Path,
        image_name: str,
        build_args: Optional[Dict[str, str]] = None,
        stream_logs: bool = False
    ) -> str:
        """
        Build a Docker image from a Dockerfile.

        Args:
            dockerfile_path: Path to directory containing Dockerfile
            image_name: Name for the built image
            build_args: Optional build arguments
            stream_logs: Whether to stream build logs to logger.info (default: False)

        Returns:
            Image ID of the built image
        """
        try:
            logger.info(f"Building image {image_name} from {dockerfile_path}")

            # Use low-level API for streaming logs
                path=str(dockerfile_path),
            response = self._docker_client.api.build(
                tag=image_name,
                buildargs=build_args,
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
        stream_logs: bool = False
    ) -> ContainerResult:
        """
        Run a container with the given configuration.

        Args:
            config: Container configuration
            timeout: Optional timeout in seconds
            stream_logs: Whether to stream container logs to logger.info (default: False)

        Returns:
            ContainerResult with execution details
        """
        container = None
        try:
            logger.debug(f"Running container {config.image} with command {config.command}")

            container = self._docker_client.containers.run(
                image=config.image,
                command=config.command,
                environment=config.environment,
                volumes=config.volumes,
                working_dir=config.working_dir,
                network_mode=config.network_mode,
                remove=config.remove,
                detach=True,
            )

            return await self._wait_for_container(container, timeout or config.timeout, stream_logs)
        except DockerException as e:
            logger.error(f"Docker error: {e}")
            raise
        except Exception as e:
            logger.error(f"Container execution error: {e}")
            raise
        finally:
            # Handle orphaned containers - only if remove=False and container still exists
            if container and not config.remove:
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
        stream_logs: bool
    ) -> ContainerResult:
        """Wait for a detached container to complete while streaming logs."""
        try:
            logs = []
            log_stream = container.logs(stdout=True, stderr=True, stream=True, follow=True)
            log_task = asyncio.create_task(
                self._stream_container_logs(log_stream, logs, container.id, stream_logs)
            )

            exit_code = await self._wait_for_container_completion(container, timeout)

            await self._cleanup_log_task(log_task)
            await self._collect_remaining_logs(container, logs)

            full_logs = '\n'.join(logs)

            return ContainerResult(
                exit_code=exit_code,
                stdout=full_logs,
                stderr='',
                logs=logs,
                container_id=container.id
            )

        except Exception as e:
            logger.error(f"Error waiting for container {container.id}: {e}")
            raise

    async def _stream_container_logs(
        self,
        log_stream,
        logs_buffer: list,
        container_id: str,
        stream_logs: bool
    ):
        """Stream logs from container in real-time."""
        try:
            for log_chunk in log_stream:
                log_line = log_chunk.decode('utf-8', errors='ignore').strip()
                logs_buffer.append(log_line)
                if stream_logs:
                    logger.info(f"[Container {container_id[:12]}] {log_line}")
        except Exception as e:
            logger.warning(f"Error streaming logs: {e}")

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

    async def _collect_remaining_logs(self, container, logs_buffer: list):
        """Collect any remaining logs from the container."""
        try:
            # Check if container is still accessible and not dead/marked for removal
            container.reload()
            if container.status not in ['dead', 'removing', 'removed']:
                remaining_logs = container.logs(stdout=True, stderr=True).decode('utf-8', errors='ignore')
                if remaining_logs:
                    remaining_lines = remaining_logs.strip().split('\n')
                    for line in remaining_lines:
                        logs_buffer.append(line)
        except Exception as e:
            print(f"Could not get remaining logs for container {container.id}: {e}")
            # Container might have been removed or is inaccessible
            pass
