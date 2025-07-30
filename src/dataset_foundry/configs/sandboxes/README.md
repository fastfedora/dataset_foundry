# Sandbox Environments

This directory contains sandbox configurations for running code in isolated Docker containers.

## Overview

Sandbox environments provide isolated, reproducible environments for running code. This is useful for:

- Ensuring consistent execution environments across different machines
- Isolating dependencies from the host system
- Running code in controlled environments with specific versions or dependencies
- Preventing environment pollution between different executions

## Available Sandboxes

### Python Sandbox (`python`)

A Python 3.11 environment with common development dependencies.

**Features:**
- Python 3.11-slim base image
- pytest, pytest-cov, pytest-mock installed for testing
- Non-root user for security

**Configuration:**
- Image: `python-sandbox:latest`
- Working directory: `/workspace`
- Default command: `python`

## Usage

### In Pipeline Actions

```python
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests

# Run unit tests in sandbox
run_unit_tests(
    filename="test.py",
    sandbox="python",  # Use the python sandbox
    timeout=600,  # 10 minute timeout
    stream_logs=True,  # Stream container logs
    property="test_result"
)
```

### Direct Sandbox Usage

```python
from dataset_foundry.utils.docker.sandbox_runner import SandboxRunner

# Run arbitrary Python code in sandbox
sandbox_runner = SandboxRunner("python")

result = await sandbox_runner.run(
    target_file=Path("script.py"),
    workspace_dir=Path("workspace"),
    command=["python", "script.py"],
    timeout=300,
    stream_logs=True
)
```

### Parameters

- `sandbox`: Name of the sandbox configuration within `configs/sandboxes`
- `timeout`: Timeout for execution in seconds (default: 300)
- `stream_logs`: Whether to stream container logs to console
- `property`: Property name to store results

## Creating Custom Sandboxes

To create a custom sandbox:

1. Create a new directory under `configs/sandboxes/`
2. Add a `Dockerfile` for the sandbox environment
3. Add a `sandbox.yml` configuration file
4. Optionally add additional files (requirements.txt, etc.)

## How It Works

1. **Image Building**: The sandbox Docker image is built if it doesn't exist
2. **Container Execution**: A container is started with the workspace directory mounted as a volume
3. **Code Execution**: Code is executed inside the container using the specified command
4. **Result Parsing**: Container output is parsed into `SandboxResult` format
5. **Cleanup**: The container is automatically removed after execution

## Security Considerations

- Sandboxes run as non-root users when possible
- Containers are automatically removed after execution
- Temporary workspaces are cleaned up after use
- Network access can be restricted if needed

## Troubleshooting

### Common Issues

1. **Docker not running**: Ensure Docker daemon is running
2. **Image build failures**: Check Dockerfile syntax and dependencies
3. **Permission issues**: Ensure Docker has access to the workspace directory
4. **Timeout issues**: Increase timeout in sandbox configuration

### Debugging

Enable `stream_logs=True` to see container output in real-time:

```python
run_unit_tests(
    filename="test.py",
    sandbox="python",
    stream_logs=True
)
```
