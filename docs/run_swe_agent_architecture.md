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
    instructions=Key("context.swe_agent.instructions"),
    prompt=Key("context.prompts.implement_spec"),
    spec=Key("spec"),
    output_dir=Key("context.output_dir"),
    agent=Key("context.swe_agent.type"),
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
    stream_logs=True,
)
```

## Agent Configuration

### Built-in Agents

#### Codex Agent (`codex`)
- **Purpose**: OpenAI's Codex for code generation
- **Image**: `codex-agent:latest`
- **Entrypoint**: `["bash", "-c", "cat input/prompt.md | codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"]`
- **Capabilities**: AI-powered code generation using OpenAI's Codex
- **Requirements**: `OPENAI_API_KEY` environment variable

#### Claude Code Agent (`claude_code`)
- **Purpose**: Anthropic's Claude for code generation
- **Image**: `claude-code-agent:latest`
- **Command**: `["cat input/prompt.md | claude --verbose -p --output-format stream-json --dangerously-skip-permissions"]`
- **Capabilities**: AI-powered code generation using Anthropic's Claude
- **Requirements**: `ANTHROPIC_API_KEY` environment variable
- **Special Features**: JSON log formatting, network capabilities

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

The `agent.yml` file should contain at a minimum:

```yaml
container:
  image: "my-custom-agent:latest"
  # `input/prompt.md` contains the prompt for the agent to execute
  entrypoint: ["python", "-m", "agent.main", "input/prompt.md"]
  # Optional: specify working directory
  working_dir: "/workspace"
  # Optional: environment variables
  environment:
    CUSTOM_VAR: "value"
  # Optional: capabilities
  cap_add:
    - NET_ADMIN
```

The agent runner will automatically load the configuration from this path. All agent behavior,
including command structure, environment variables, and execution patterns, is defined in the
`agent.yml` file.

The working directory must be configured either in the Dockerfile via `WORKDIR` or via the
`container.working_dir` key in `agent.yml`.

### Environment Variables

Some agents require environment variables to function properly. The agent runner supports
environment variable substitution:

```yaml
container:
  environment:
    OPENAI_API_KEY: "${OPENAI_API_KEY}"  # Will be replaced with system environment variable
    CUSTOM_VAR: "static_value"           # Will be used as-is
```

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

- **input/AGENTS.md**: General operating instructions
- **input/prompt.md**: Task-specific prompt (created by the action)
- **input/spec.yaml**: Specification data (JSON/YAML)
- **repo/**: Optional existing repository

### Typical Output Structure

```
output_dir/
├── input/
│   ├── AGENTS.md
│   ├── prompt.md
│   └── spec.yaml
└── repo/
    └── (generated repo files)
```

### Result Data

The action stores results in item data:

```python
{
    "agent_result": AgentResult,
}
```

## Parameters

### Required Parameters
- **instructions**: General operating instructions for the agent (rendered as AGENTS.md)
- **prompt**: The specific prompt that references the spec
- **spec**: Specification data (string or dict, rendered as JSON/YAML)
- **output_dir**: Directory where agent output should be saved
- **agent**: Name of the agent to run (e.g., "codex", "claude_code")

### Optional Parameters
- **repo_path**: Optional path to pre-existing repository
- **timeout**: Maximum execution time in seconds (default: 3600)
- **max_retries**: Maximum number of retry attempts (default: 3)
- **output_key**: Key to store the agent result in item data (default: "agent_result")
- **stream_logs**: Whether to stream container logs to logger.info (default: False)

### Default Parameter Resolution
The action uses dataset_foundry's parameter resolution system with these defaults:
- `instructions`: `Key("context.swe_agent.instructions")`
- `prompt`: `Key("context.prompts.implement_spec")`
- `spec`: `Key("spec")`
- `output_dir`: `Key("context.output_dir")`
- `agent`: `Key("context.swe_agent.type")`
