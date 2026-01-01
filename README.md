# Farm Code

**AI agent orchestration platform for complete SDLC management**

Farm Code orchestrates specialized AI agents through an 8-phase software delivery workflow, from architecture design through deployment. Built on git worktrees, GitHub-centric communication, and test-driven development.

## Features

| Feature | Description |
|---------|-------------|
| **8-Phase Workflow** | Structured delivery: Setup → Specs → Plans → Tests → Implementation → PR → Review → Merge |
| **4 Human Approval Gates** | Control points after specs, plans, tests, and final review |
| **Git Worktrees** | Isolated feature workspaces as sibling directories |
| **GitHub-Centric** | All communication via issue comments for full transparency |
| **TDD Implementation** | Tests written first, code loops until tests pass |
| **MCP Integration** | Agents use Model Context Protocol for tracker-agnostic communication |
| **Multi-Agent Parallel** | Agents work simultaneously on backend, frontend, infrastructure |
| **Desktop UI** | Kanban board, agent terminals, real-time workflow visualization |
| **GitOps Ready** | Integrates with ArgoCD for automatic deployments |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FARM CODE DESKTOP APP                        │
│                   (Electron + React + Python)                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Kanban Board │  │ Agent Terms  │  │ Approval Gates      │  │
│  │ (8 phases)   │  │ (Live output)│  │ (Human checkpoints) │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Python State Machine)                │
│                                                                 │
│  Phase Manager → Agent Dispatcher → Worktree Manager           │
│       ↓               ↓                    ↓                    │
│  8 Phases      Claude CLI Spawn     Git Worktree Mgmt          │
└──────┬──────────────────┬────────────────────┬─────────────────┘
       │                  │                    │
       ▼                  ▼                    ▼
┌─────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   GitHub    │  │  Farmcode MCP    │  │  Git Worktrees  │
│   Issues    │  │     Server       │  │  (per feature)  │
│  Comments   │  │  (Embedded)      │  │                 │
│   Labels    │  │                  │  │  123-feature/   │
└─────────────┘  └────────┬─────────┘  │  456-bugfix/    │
                          │            └─────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Issue Tracker        │
              │  Adapter Layer        │
              │                       │
              │  • GitHubAdapter      │
              │  • JiraAdapter        │
              │  • LinearAdapter      │
              └───────────────────────┘
```

## Agents

Each agent is a specialized Claude Code subprocess with domain expertise:

| Handle | Name | Role | GitHub App |
|--------|------|------|------------|
| @baron | Baron Haussmann | PM/Orchestrator | farmcode-baron |
| @veuve | Veuve Clicquot | Product Owner | farmcode-veuve |
| @duc | Viollet-le-Duc | Architect | farmcode-duc |
| @dede | André Citroën | Backend Dev | farmcode-dede |
| @dali | Salvador Dalí | Frontend Dev | farmcode-dali |
| @gus | Gustave Eiffel | DevOps | farmcode-gus |
| @marie | Marie Marvingt | QA | farmcode-marie |

## Workflow Phases

```
PHASE 1: Issue & Worktree Creation (Program)
    ↓
PHASE 2: Architecture & Specs (@duc)
    ↓
⛔ GATE 1: Human Approval (Specs)
    ↓
PHASE 3: Implementation Plans (@dede, @dali, @gus in parallel)
    ↓
⛔ GATE 2: Human Approval (Plans)
    ↓
PHASE 4: Test Design (@marie)
    ↓
⛔ GATE 3: Human Approval (Tests)
    ↓
PHASE 5: Implementation (@dede, @dali, @gus - TDD loop)
    ↓
PHASE 6: Create PR (Program)
    ↓
PHASE 7: Review (@dede, @dali, @gus, @marie)
    ↓
⛔ GATE 4: Human Approval (Merge)
    ↓
PHASE 8: Merge & Cleanup (Program + ArgoCD deploy)
```

## Project Structure

```
farmcode/
├── apps/
│   ├── backend/              # Python orchestrator + MCP server
│   │   ├── farmcode/
│   │   │   ├── orchestrator/  # State machine, phase manager
│   │   │   ├── mcp/           # MCP server implementation
│   │   │   ├── adapters/      # GitHub/Jira/Linear adapters
│   │   │   ├── git/           # Worktree manager
│   │   │   └── agents/        # Agent dispatcher
│   │   └── pyproject.toml
│   │
│   └── frontend/             # Electron desktop app
│       ├── src/
│       │   ├── main/          # Electron main process
│       │   ├── renderer/      # React UI
│       │   └── shared/        # Shared types
│       └── package.json
│
├── docs/
│   ├── mcp-tools-spec.md      # MCP tool specifications
│   └── sdlc-workflow.md       # Workflow documentation
│
└── references/
    ├── autoclaude-ui.png      # UI reference
    └── sdlc-workflow.md       # Workflow spec
```

## Installation

### Prerequisites

- **Node.js 24+** - For Electron app
- **Python 3.12+** - For orchestrator
- **Claude Code CLI** - `npm install -g @anthropic-ai/claude-code`
- **Git 2.40+** - For worktree support
- **GitHub CLI** - `brew install gh` (or platform equivalent)
- **GitHub Apps** - One configured per agent with bot accounts

### Setup

```bash
# Clone the repository
git clone https://github.com/farmer1st/farmcode.git
cd farmcode

# Install backend dependencies
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -e .

# Install frontend dependencies
cd ../frontend
npm install

# Configure GitHub Apps
# See docs/github-app-setup.md for details

# Run in development mode
npm run dev
```

## Configuration

Environment variables (in `apps/backend/.env`):

```bash
# GitHub Configuration
FARMCODE_REPO=farmer1st/farmer1st-platform
FARMCODE_GITOPS_REPO=farmer1st/farmer1st-gitops
FARMCODE_AI_AGENTS_REPO=farmer1st/farmer1st-ai-agents

# Agent GitHub App Credentials (one per agent)
FARMCODE_BARON_APP_ID=123456
FARMCODE_BARON_PRIVATE_KEY_PATH=/path/to/baron-key.pem
FARMCODE_DUC_APP_ID=123457
FARMCODE_DUC_PRIVATE_KEY_PATH=/path/to/duc-key.pem
# ... (similar for dede, dali, gus, marie)

# Claude Configuration
CLAUDE_CODE_MODEL=claude-sonnet-4-20250514

# Orchestrator Settings
FARMCODE_POLL_INTERVAL=10  # GitHub comment polling interval (seconds)
FARMCODE_WORKTREE_BASE_PATH=~/Dev/farmer1st/github
```

## Usage

### Starting the Desktop App

```bash
npm run dev
```

The app will:
1. Start the Python orchestrator backend
2. Launch the Electron frontend
3. Connect to your configured GitHub repository
4. Show existing issues/features on the Kanban board

### Creating a New Feature

1. Click "New Feature" in the app
2. Enter feature description and acceptance criteria
3. App creates GitHub issue, branch, and worktree
4. Orchestrator automatically dispatches @duc for architecture specs
5. Monitor progress on Kanban board and agent terminals
6. Approve at each gate when ready

### CLI Usage (Alternative)

For headless operation or scripting:

```bash
cd apps/backend

# Create a new feature
python -m farmcode create-feature "Add user authentication"

# Monitor active features
python -m farmcode status

# Manually approve a gate
python -m farmcode approve 123 --gate specs
```

## Development

```bash
# Backend development
cd apps/backend
pip install -e ".[dev]"
pytest
ruff check farmcode/

# Frontend development
cd apps/frontend
npm run dev
npm test
npm run lint
```

## Documentation

- [SDLC Workflow](./references/sdlc-workflow.md) - Complete 8-phase workflow specification
- [MCP Tools](./docs/mcp-tools-spec.md) - MCP server tool documentation
- [GitHub App Setup](./docs/github-app-setup.md) - Configuring agent GitHub Apps
- [Architecture](./docs/architecture.md) - System architecture deep dive

## License

MIT

---

**Built for Farmer1st by the Farmer1st team** 🚜
