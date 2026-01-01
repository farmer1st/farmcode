# Farm Code Backend

Python backend for Farm Code - AI Agent Orchestration Platform.

## Overview

The backend orchestrates AI agents through an 8-phase SDLC workflow:
- Phase 1: Setup (issue + worktree creation)
- Phase 2: Architecture specs (@duc)
- Gate 1: Human approval
- Phase 3-8: Implementation, review, QA, deployment (future)

## Components

### Orchestrator
Main coordination layer that manages workflow state transitions and agent dispatch.

**Key Files**:
- [`orchestrator/orchestrator.py`](farmcode/orchestrator/orchestrator.py) - Main orchestrator
- [`orchestrator/state_machine.py`](farmcode/orchestrator/state_machine.py) - Phase transitions
- [`orchestrator/phase_manager.py`](farmcode/orchestrator/phase_manager.py) - Phase execution
- [`orchestrator/agent_dispatcher.py`](farmcode/orchestrator/agent_dispatcher.py) - Agent spawning
- [`orchestrator/github_poller.py`](farmcode/orchestrator/github_poller.py) - Comment monitoring

### MCP Server
Model Context Protocol server providing tools for agent communication.

**Key Files**:
- [`mcp/server.py`](farmcode/mcp/server.py) - MCP server with 3 tools

**Available Tools**:
- `task_get_context(issue_number)` - Get issue details
- `task_post_comment(issue_number, comment)` - Post comments
- `task_signal_complete(issue_number, summary, artifacts)` - Mark complete

### Git Operations
Manages git worktrees for isolated feature development.

**Key Files**:
- [`git/worktree_manager.py`](farmcode/git/worktree_manager.py) - Worktree creation

### Storage
State persistence to JSON files.

**Key Files**:
- [`storage/state_store.py`](farmcode/storage/state_store.py) - Feature state persistence

**Storage Location**: `~/.farmcode/features/{issue_number}.json`

### Models
Pydantic models for workflow state and phases.

**Key Files**:
- [`models/state.py`](farmcode/models/state.py) - FeatureState, PhaseState
- [`models/phase.py`](farmcode/models/phase.py) - WorkflowPhase enum

### Adapters
GitHub integration via `gh` CLI.

**Key Files**:
- [`adapters/github_adapter.py`](farmcode/adapters/github_adapter.py) - GitHub operations

### Configuration
YAML-based configuration management.

**Key Files**:
- [`config.py`](farmcode/config.py) - Configuration loader
- [`config/farmcode.yaml`](config/farmcode.yaml) - Main settings
- [`config/agents.yaml`](config/agents.yaml) - Agent credentials

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv venv
uv pip install -e ".[dev]"
```

## Configuration

### Required Files

1. **farmcode.yaml** - Main configuration
2. **agents.yaml** - Agent credentials
3. **Agent keys** - `.pem` files in `~/Dev/farmer1st/github/.keys/`

### Setup Steps

1. Copy config files:
```bash
cp config/farmcode.yaml.example config/farmcode.yaml
cp config/agents.yaml.example config/agents.yaml
```

2. Update repository names in `farmcode.yaml`
3. Ensure `.pem` files exist in keys directory
4. Verify `gh-agent` script is accessible

## Usage

### CLI Commands

```bash
# Create a feature
farmcode create "Add dark mode" "Implement dark mode toggle in settings"

# List all features
farmcode list

# Show feature details
farmcode show 123

# Approve a gate
farmcode approve 123

# Run orchestrator polling loop
farmcode run --interval 10
```

### Programmatic Usage

```python
from farmcode.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator()

# Create a feature
state = orchestrator.create_feature(
    title="Add user authentication",
    description="Implement JWT-based authentication"
)

print(f"Feature #{state.issue_number} created")
print(f"Phase: {state.current_phase.value}")

# Approve a gate
orchestrator.approve_gate(state.issue_number)

# Run polling loop
import asyncio
asyncio.run(orchestrator.run_polling_loop())
```

### MCP Server (Standalone)

```bash
# Run MCP server on default port (8000)
uv run python -m farmcode.mcp.server

# Custom host/port
FARMCODE_MCP_HOST=0.0.0.0 FARMCODE_MCP_PORT=9000 uv run python -m farmcode.mcp.server
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=farmcode --cov-report=html

# Run specific test file
uv run pytest tests/test_state_machine.py -v
```

### Type Checking

```bash
uv run mypy farmcode
```

### Linting

```bash
uv run ruff check farmcode
uv run ruff format farmcode
```

## Architecture

```
farmcode/
├── orchestrator/          # Workflow orchestration
│   ├── orchestrator.py    # Main coordinator
│   ├── state_machine.py   # Phase transitions
│   ├── phase_manager.py   # Phase execution
│   ├── agent_dispatcher.py # Agent spawning
│   └── github_poller.py   # Comment monitoring
├── mcp/                   # MCP server
│   └── server.py          # FastMCP server
├── git/                   # Git operations
│   └── worktree_manager.py
├── storage/               # State persistence
│   └── state_store.py
├── models/                # Data models
│   ├── state.py
│   └── phase.py
├── adapters/              # External integrations
│   ├── github_adapter.py
│   └── base.py
├── config.py              # Configuration loader
└── cli.py                 # CLI interface
```

## How It Works

### Workflow Flow

1. **Feature Creation**:
   - User creates feature via CLI/UI
   - Orchestrator executes Phase 1:
     - Creates GitHub issue
     - Creates git branch and worktree
     - Initializes `.plans/` folder structure
   - Auto-advances to Phase 2

2. **Phase 2 Execution**:
   - Phase manager posts comment mentioning @duc
   - Agent dispatcher spawns Claude CLI with MCP config
   - @duc uses MCP tools to:
     - Get issue context
     - Write specs to `.plans/{issue}/specs/`
     - Signal completion

3. **Completion Detection**:
   - GitHub poller monitors comments for ✅ marker
   - Detects @duc completion
   - State machine validates all agents complete
   - Auto-advances to Gate 1

4. **Gate 1 Approval**:
   - Phase manager posts approval request
   - Human reviews specs
   - Approves via CLI/UI or GitHub comment
   - Auto-advances to Phase 3 (future)

### Agent Dispatch

Agents are spawned as Claude CLI processes with MCP configuration:

```bash
claude \
  --model sonnet \
  --prompt "Review issue #123..." \
  # MCP server URL passed via env
```

Environment variables:
- `FARMCODE_AGENT_HANDLE` - Agent identity (e.g., "duc")
- `FARMCODE_MCP_SERVER_URL` - MCP server endpoint
- `FARMCODE_ISSUE_NUMBER` - GitHub issue number

### State Persistence

Feature states are persisted to `~/.farmcode/features/{issue_number}.json`:

```json
{
  "issue_number": 123,
  "title": "Add dark mode",
  "branch_name": "123-add-dark-mode",
  "worktree_path": "/Users/lol/Dev/farmer1st/github/123-add-dark-mode",
  "current_phase": "PHASE_2_SPECS",
  "phase_history": [...]
}
```

## Troubleshooting

### Agent keys not found
Ensure `.pem` files exist in `~/Dev/farmer1st/github/.keys/`:
```bash
ls ~/Dev/farmer1st/github/.keys/
# Should show: duc.pem, baron.pem, etc.
```

### gh-agent script not found
Update path in `config/farmcode.yaml`:
```yaml
paths:
  gh_agent_script: "~/Dev/farmer1st/github/farmer1st-developer-toolkit/utilities/gh-agent"
```

### MCP server connection failed
Check MCP server is running:
```bash
curl http://127.0.0.1:8000/health
```

## Future Enhancements

- [ ] Phase 3-8 implementation
- [ ] Multi-agent parallel execution
- [ ] Agent session resumption
- [ ] Error recovery and retry logic
- [ ] Webhook support (replace polling)
- [ ] Desktop app integration (Electron IPC)
