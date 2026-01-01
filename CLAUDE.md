# Farm Code - AI Agent Orchestration Platform

## Project Overview

Farm Code is a desktop application (Electron + Python) that orchestrates specialized AI agents through an 8-phase Software Development Life Cycle (SDLC) workflow. It manages features from design through deployment with full transparency via GitHub issue comments.

**Status**: MVP in development (Phase 1, 2, Gate 1)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ELECTRON DESKTOP APP                       │
├───────────────────┬─────────────────────────────────────┤
│  Main Process     │  Renderer Process                   │
│  (Node.js)        │  (React + Zustand)                  │
├───────────────────┼─────────────────────────────────────┤
│  OrchestratorMgr  │  Kanban Board (3 columns)          │
│  WorktreeMgr      │  Agent Terminals                    │
│  IPC Handlers     │  Feature Cards                      │
└───────────────────┴─────────────────────────────────────┘
         │                         │
         ▼                         ▼
   Python Backend           Claude CLI Agents
   (FastAPI + MCP)          (@duc, @baron, etc.)
         │
         ▼
   GitHub API (via gh CLI)
```

---

## Repository Structure

```
farmcode/
├── apps/
│   ├── backend/              # Python orchestrator
│   │   ├── farmcode/
│   │   │   ├── orchestrator/ # State machine, phase manager
│   │   │   ├── mcp/          # MCP server for agents
│   │   │   ├── git/          # Worktree manager
│   │   │   ├── storage/      # State persistence
│   │   │   ├── models/       # Pydantic models
│   │   │   ├── adapters/     # GitHub adapter
│   │   │   └── config.py     # YAML config loader
│   │   ├── config/
│   │   │   ├── farmcode.yaml # Main settings
│   │   │   └── agents.yaml   # Agent credentials
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── e2e/
│   │   └── pyproject.toml
│   │
│   └── frontend/             # Electron app (NOT YET IMPLEMENTED)
│       ├── src/
│       │   ├── main/         # Electron main process
│       │   ├── renderer/     # React UI
│       │   └── preload/      # IPC bridge
│       └── package.json
│
├── docs/
│   ├── specs/                # Feature specifications
│   ├── mcp-tools-spec.md     # MCP tool definitions
│   └── sdlc-workflow.md      # 8-phase workflow spec
│
├── references/               # Reference implementations
│   └── sdlc-workflow.md
│
├── DEVELOPMENT.md            # Development methodology
├── CLAUDE.md                 # This file
└── README.md
```

---

## Development Methodology

**MANDATORY**: Follow Spec-Driven + Test-Driven Development

### Workflow for Every Feature

1. **Specification Phase**
   - Write spec in `docs/specs/`
   - **GATE**: User approval required

2. **Test Phase**
   - Write tests: Unit → Integration → E2E
   - Organize in `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - **GATE**: User validates coverage

3. **Verification Phase**
   - Run tests → ALL MUST FAIL (red phase)
   - Confirm failures are intentional
   - **GATE**: User confirms

4. **Implementation Phase**
   - TDD: One test at a time
   - Write minimal code to pass
   - Refactor while keeping green

5. **Validation Phase**
   - Run full test suite with coverage
   - Run linting + type checking
   - **GATE**: User acceptance

**See [DEVELOPMENT.md](DEVELOPMENT.md) for complete methodology**

---

## Tech Stack

### Backend (Python)
- **Framework**: FastAPI (for MCP server)
- **MCP**: Model Context Protocol SDK
- **Git**: GitPython
- **Config**: PyYAML + Pydantic
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Linting**: ruff + mypy
- **Python**: 3.12+

### Frontend (Electron) - NOT YET IMPLEMENTED
- **Desktop**: Electron
- **UI**: React + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **GitHub**: Issue tracking, comments, labels
- **Git Worktrees**: Isolated feature development
- **MCP Server**: Agent communication
- **Claude CLI**: Agent execution

---

## Key Concepts

### 8-Phase SDLC Workflow

1. **Phase 1: Setup** - Create issue, branch, worktree
2. **Phase 2: Specs** - @duc writes architecture specs
3. **Gate 1: Spec Approval** - Human reviews specs
4. **Phase 3: Plans** - @baron creates implementation plans *(not implemented)*
5. **Gate 2: Plan Approval** - Human reviews plans *(not implemented)*
6. **Phase 4: Implementation** - @dede writes code *(not implemented)*
7. **Gate 3: Code Review** - Human reviews PR *(not implemented)*
8. **Phase 5: QA** - @marie runs tests *(not implemented)*
9. **Gate 4: QA Approval** - Human approves release *(not implemented)*

### Git Worktrees
- Each feature gets isolated worktree
- Branch naming: `{issue-number}-{slug}`
- Location: `~/Dev/farmer1st/github/{branch-name}`
- Structure: `.plans/{issue}/specs|plans|reviews|qa/`

### MCP (Model Context Protocol)
- Agents communicate via MCP server
- Tools available to agents:
  - `task_get_context(issue_number)` - Get issue details
  - `task_post_comment(issue_number, comment)` - Post updates
  - `task_signal_complete(issue_number, summary, artifacts)` - Mark done

### GitHub Communication
- All agent updates via issue comments
- Emoji markers:
  - ✅ - Task complete
  - ❓ - Question for team
  - 🚫 - Blocked
- Labels track phase: `phase:1-setup`, `phase:2-specs`, etc.

---

## Configuration

### farmcode.yaml
Main configuration for repositories, paths, orchestrator settings.

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
Agent GitHub App credentials (app_id, install_id).

```yaml
agents:
  duc:
    name: "Viollet-le-Duc"
    app_id: "2557336"
    install_id: "101694538"
    model: "sonnet"
```

**Note**: Private keys (`.pem` files) live in `~/Dev/farmer1st/github/.keys/{agent}.pem`

---

## Agent Ecosystem

### Specialized Agents
- **@duc** (Viollet-le-Duc) - Architecture specs
- **@baron** (Baron Haussmann) - Implementation plans
- **@dede** (André Déde) - Code implementation
- **@dali** (Salvador Dali) - Frontend/UI
- **@marie** (Marie Curie) - Testing/QA
- **@gustave** (Gustave Eiffel) - DevOps/Infrastructure
- **@charles** (Charles Martel) - Security
- **@louis** (Louis Pasteur) - Networking

Each agent has:
- GitHub App bot account
- Private key for authentication
- Specialized knowledge/skills
- MCP tools for communication

---

## Running the Backend

### Installation
```bash
cd apps/backend
pip install -e ".[dev]"
```

### Configuration
1. Ensure `config/farmcode.yaml` exists
2. Ensure `config/agents.yaml` exists
3. Ensure `.pem` files in `~/Dev/farmer1st/github/.keys/`
4. Verify `gh-agent` script accessible

### CLI Usage
```bash
# Create a feature
farmcode create "Add User Auth" "Implement JWT authentication"

# List features
farmcode list

# Show feature details
farmcode show 123

# Approve a gate
farmcode approve 123

# Run orchestrator polling loop
farmcode run --interval 10
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=farmcode --cov-report=html

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific test
pytest tests/e2e/test_mvp_integration.py::test_mvp_workflow_end_to_end -v
```

### Linting
```bash
# Check code
ruff check farmcode

# Format code
ruff format farmcode

# Type checking
mypy farmcode
```

---

## Frontend (NOT YET IMPLEMENTED)

The Electron frontend will provide:
- **Kanban Board**: Drag-and-drop feature management
- **Agent Terminals**: Read-only view of agent output
- **Feature Cards**: Status, phase, approval buttons
- **Real-time Updates**: WebSocket or IPC events

Based on Auto-Claude architecture patterns.

---

## GitHub Integration

### Authentication
Uses GitHub Apps (one per agent) with `gh-agent` wrapper:
```bash
# gh-agent handles JWT generation + installation token
gh-agent duc issue create --repo farmer1st/platform --title "..."
```

### Issue Structure
```
Title: Add User Authentication
Body: Feature description
Labels: farmcode, phase:2-specs
Comments:
  - 🚀 Farm Code initialized (orchestrator)
  - 📋 Phase 2 started (@orchestrator)
  - ✅ Task complete (@duc)
  - ⏸️ Gate 1: Approval required (@orchestrator)
  - approved (@human)
```

### Branch Structure
```
main
└── 123-add-user-authentication (feature branch)
    └── .plans/123/
        ├── README.md
        ├── specs/      (Phase 2 - @duc)
        ├── plans/      (Phase 3 - @baron)
        ├── reviews/    (Phase 4 - @dede)
        └── qa/         (Phase 5 - @marie)
```

---

## State Management

### Persistence
States stored in: `~/.farmcode/features/{issue_number}.json`

### State Model
```json
{
  "issue_number": 123,
  "title": "Add User Authentication",
  "description": "...",
  "branch_name": "123-add-user-authentication",
  "worktree_path": "/Users/.../github/123-add-user-authentication",
  "current_phase": "PHASE_2_SPECS",
  "phase_history": [
    {
      "phase": "PHASE_1_SETUP",
      "started_at": "2025-01-01T10:00:00",
      "completed_at": "2025-01-01T10:01:00",
      "agents_complete": [],
      "approved": true
    }
  ]
}
```

---

## Important Files

### Backend
- [config.py](apps/backend/farmcode/config.py) - Configuration loader
- [orchestrator.py](apps/backend/farmcode/orchestrator/orchestrator.py) - Main coordinator
- [state_machine.py](apps/backend/farmcode/orchestrator/state_machine.py) - Phase transitions
- [phase_manager.py](apps/backend/farmcode/orchestrator/phase_manager.py) - Phase execution
- [agent_dispatcher.py](apps/backend/farmcode/orchestrator/agent_dispatcher.py) - Agent spawning
- [github_poller.py](apps/backend/farmcode/orchestrator/github_poller.py) - Comment monitoring
- [server.py](apps/backend/farmcode/mcp/server.py) - MCP server
- [worktree_manager.py](apps/backend/farmcode/git/worktree_manager.py) - Git operations

### Documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development methodology
- [mcp-tools-spec.md](docs/mcp-tools-spec.md) - MCP tool specifications
- [sdlc-workflow.md](references/sdlc-workflow.md) - Workflow specification

### Configuration
- [farmcode.yaml](apps/backend/config/farmcode.yaml) - Main settings
- [agents.yaml](apps/backend/config/agents.yaml) - Agent credentials

---

## Common Tasks

### Add a New Agent
1. Create GitHub App for agent
2. Download `.pem` key to `~/.keys/{agent}.pem`
3. Add to `config/agents.yaml`:
   ```yaml
   agents:
     newagent:
       name: "New Agent Name"
       app_id: "123456"
       install_id: "789012"
       model: "sonnet"
   ```

### Add a New Phase
1. Write spec in `docs/specs/phase-N-{name}.md`
2. Get approval
3. Write tests (unit → integration → e2e)
4. Verify all fail
5. Update `WorkflowPhase` enum in `models/phase.py`
6. Add phase execution in `phase_manager.py`
7. Update state machine transitions
8. Implement until tests pass

### Debug Agent Issues
1. Check agent session: `orchestrator.agent_dispatcher.get_all_sessions()`
2. Check MCP server logs
3. Verify `.pem` file exists
4. Test `gh-agent` manually:
   ```bash
   gh-agent duc issue list --repo farmer1st/platform
   ```

### Reset State
```bash
# Clear all feature states
rm -rf ~/.farmcode/features/*

# Delete worktrees
git worktree list
git worktree remove {path}
```

---

## Known Limitations (MVP)

- ✅ Phase 1, 2, Gate 1 implemented
- ❌ Phase 3-8 not implemented yet
- ❌ Frontend not implemented yet
- ❌ Multi-agent parallel execution not implemented
- ❌ Agent session resumption not implemented
- ❌ Error recovery not implemented
- ❌ Webhook support not implemented (polling only)

---

## Dependencies

### External Services
- **GitHub API** - Issue/comment management
- **Claude API** - Agent intelligence
- **Git** - Version control

### External Tools
- **gh CLI** - GitHub operations
- **gh-agent** - GitHub App authentication wrapper
- **git** - Worktree management

### Python Packages
See [pyproject.toml](apps/backend/pyproject.toml)

---

## Troubleshooting

### "Agent key not found"
- Check `.pem` file exists: `ls ~/Dev/farmer1st/github/.keys/`
- Verify path in `farmcode.yaml`

### "gh-agent script not found"
- Update path in `farmcode.yaml`:
  ```yaml
  paths:
    gh_agent_script: "~/Dev/farmer1st/github/farmer1st-developer-toolkit/utilities/gh-agent"
  ```

### "MCP server connection failed"
- Check server running: `curl http://127.0.0.1:8000/health`
- Restart MCP server
- Check environment variables in agent dispatch

### Tests failing
```bash
# Clear pytest cache
rm -rf .pytest_cache __pycache__

# Reinstall in dev mode
pip install -e ".[dev]"

# Run with verbose output
pytest -vv
```

---

## Next Steps

### Immediate (MVP Completion)
1. ✅ Backend core complete
2. ✅ Tests complete
3. ⏳ Test backend manually
4. ⏳ Build Electron frontend
5. ⏳ Test end-to-end workflow

### Future Phases
1. Phase 3-8 implementation
2. Multi-agent orchestration
3. Error handling and recovery
4. Webhook integration
5. Desktop app enhancements
6. CI/CD pipeline

---

## Resources

- **Auto-Claude Reference**: [github.com/cyanheads/auto-claude](https://github.com/cyanheads/auto-claude)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **FastMCP**: [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **GitPython**: [gitpython.readthedocs.io](https://gitpython.readthedocs.io)
- **Pydantic**: [docs.pydantic.dev](https://docs.pydantic.dev)

---

## Contact & Support

For questions about:
- **Product strategy**: Ask @veuve
- **Architecture**: Ask @duc
- **DevOps**: Ask @gustave
- **Testing**: Ask @marie

Or consult the farmer1st-developer-toolkit repository.
