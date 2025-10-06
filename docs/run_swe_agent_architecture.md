# `run_swe_agent` Architecture

## Overview

The `run_swe_agent` action provides a flexible, containerized approach to running software
engineering agents within the dataset_foundry framework. It supports multiple agent types and
configurable agent implementations.

## Architecture Components

### 1. Core Action (`run_swe_agent.py`)

The main action that orchestrates agent execution:

- **Parameter Resolution**: Uses dataset_foundry's parameter resolution system
- **Input Preparation**: Creates standardized input files (AGENTS.md, PROMPT.md, spec.yaml)
- **Agent Execution**: Delegates to AgentRunner for containerized execution
- **Result Processing**: Stores agent results in item data

### 2. Container Management (`container_manager.py`)

Handles Docker container lifecycle:

- **Container Execution**: Runs containers with proper configuration
- **Image Building**: Builds agent images from Dockerfiles
- **Resource Management**: Manages active containers and cleanup
- **Error Handling**: Provides robust error handling and retry logic

### 3. Agent Runner (`agent_runner.py`)

Orchestrates different agent types:

- **Configuration Loading**: Loads agent configurations from files or built-in defaults
- **Container Configuration**: Prepares container configs with proper volumes and environment
- **Result Processing**: Processes container results into standardized format
- **Agent Type Support**: Supports multiple agent types (swe_agent, refactor_agent, etc.)


## Usage Examples

### Basic Usage

```python
from dataset_foundry.actions.item.run_swe_agent import run_swe_agent

# In a pipeline
run_swe_agent(
    instructions=Key("context.agents.instructions"),
    prompt=Key("context.prompts.implement_spec"),
    spec=Key("spec"),
    output_dir=Template("{context.output_dir}/{id}"),
    agent=Key("context.agents.agent"),
)
```

### Configuration

```yaml
# config.yaml
swe_agent:
  type: "codex"
  instructions: |-
    # Agent instructions here
    You are a software engineering agent...

prompts:
  implement_spec: |-
    # Task-specific prompt here
    Implement the following specification...
```

### Advanced Usage with Custom Agent

```python
# Custom agent configuration
run_swe_agent(
    instructions="Custom agent instructions",
    prompt="Custom prompt",
    spec={"name": "my_project", "files": [...]},
    output_dir="/path/to/output",
    agent="custom_agent",
    repo_path="/path/to/existing/repo",
    timeout=7200,
    max_retries=5,
    output_key="custom_result",
)
```

## Agent Configuration

### Built-in Agents

#### Codex Agent (`codex`)
- **Purpose**: OpenAI's Codex for code generation
- **Image**: `codex-agent:latest`
- **Entrypoint**: `bash -c "cat /workspace/PROMPT.md | codex exec --skip-git-repo-check"`
- **Capabilities**: AI-powered code generation using OpenAI's Codex
- **Requirements**: `OPENAI_API_KEY` environment variable

### Custom Agent Configuration

The agent configuration is automatically derived from the agent name. For example, if you specify
`agent="my_custom_agent"`, the system will look for configuration in
`src/dataset_foundry/configs/agents/my_custom_agent/agent.yml`.

To add a custom agent, create the directory structure:

```
configs/agents/my_custom_agent/
├── agent.yml          # Agent configuration
├── Dockerfile         # Docker image definition
└── agent/
    └── main.py        # Custom agent entry point, if not installed by Dockerfile
```

The `agent.yml` file should contain:

```yaml
image: "my-custom-agent:latest"
dockerfile_path: "src/dataset_foundry/configs/agents/my_custom_agent"
working_dir: "/workspace"
environment:
  PYTHONPATH: "/workspace"
  LANG: "en_US.UTF-8"
volumes:
  "/tmp": {"bind": "/tmp", "mode": "rw"}
entrypoint: ["python", "-m", "agent.main"]

# Or for a CLI tool that reads from stdin
image: "my-cli-agent:latest"
dockerfile_path: "src/dataset_foundry/configs/agents/my_cli_agent"
working_dir: "/workspace"
environment:
  API_KEY: "${API_KEY}"
volumes:
  "/tmp": {"bind": "/tmp", "mode": "rw"}
entrypoint: ["bash", "-c", "cat /workspace/PROMPT.md | my-cli-tool --config /workspace/spec.yaml"]
```

The agent runner will automatically load the configuration from this path. All agent behavior,
including command structure, environment variables, and execution patterns, is defined in the
`agent.yml` file.

### Environment Variables

Some agents require environment variables to function properly. The agent runner supports
environment variable substitution:

```yaml
environment:
  OPENAI_API_KEY: "${OPENAI_API_KEY}"  # Will be replaced with system environment variable
  CUSTOM_VAR: "static_value"           # Will be used as-is
```

The system will automatically inject environment variables from the host system into the container.

### Agent Directory Structure

```
configs/agents/
└── codex/
    ├── agent.yml          # Agent configuration
    └── Dockerfile         # Docker image definition
```

## Input/Output Interface

### Input Files

The action creates these files in the agent's workspace:

- **AGENTS.md**: General operating instructions
- **PROMPT.md**: Task-specific prompt
- **spec.yaml**: Specification data (JSON/YAML)
- **repo/**: Optional existing repository

### Typical Output Structure

```
output_dir/
├── AGENTS.md
├── PROMPT.md
├── spec.yaml
├── repo/
│   └── (generated repo files)
└── build-info
    ├── agent_metadata.yaml
    └── agent_results.yaml
```

### Result Data

The action stores results in item data:

```python
{
    "agent_result": AgentResult,
    "agent_result_metadata": {
        "agent": "codex",
        "output_dir": "/path/to/output",
        "attempts": 1,
        "success": True
    }
}
```
