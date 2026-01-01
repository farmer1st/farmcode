# Farm Code Configuration

All Farm Code configuration is managed via YAML files in this directory.

## Configuration Files

### farmcode.yaml
Main configuration for repositories, paths, and orchestrator settings.

```yaml
repository:
  main: "farmer1st/farmer1st-platform"
  gitops: "farmer1st/farmer1st-gitops"
  ai_agents: "farmer1st/farmer1st-ai-agents"

paths:
  worktree_base: "~/Dev/farmer1st/github"
  keys_dir: "~/Dev/farmer1st/github/.keys"
  gh_agent_script: "~/Dev/farmer1st/github/farmer1st-developer-toolkit/utilities/gh-agent"

orchestrator:
  poll_interval: 10
  max_parallel_agents: 4

claude:
  model: "claude-sonnet-4-20250514"
```

### agents.yaml
Agent credentials (GitHub App IDs and Installation IDs).

```yaml
agents:
  duc:
    name: "Viollet-le-Duc"
    app_id: "2557336"
    install_id: "101694538"
    model: "sonnet"
```

**Note**: Private keys (`.pem` files) are NOT in this repo. They must be in `~/Dev/farmer1st/github/.keys/{agent}.pem`

## Usage

```python
from farmcode.config import get_settings

settings = get_settings()

# Access configuration
repo = settings.repository.main  # "farmer1st/farmer1st-platform"
poll_interval = settings.orchestrator.poll_interval  # 10

# Get agent config
agent_config = settings.get_agent_config("duc")
# Returns: AgentConfig(app_id="2557336", install_id="101694538", ...)
```

## Setup

1. Copy `farmcode.yaml` and `agents.yaml` to this directory
2. Update repository names if needed
3. Ensure `.pem` files exist in `~/Dev/farmer1st/github/.keys/`
4. Farm Code will validate all paths and keys on startup
