# Data Model: Orchestrator State Machine

**Feature**: 003-orchestrator-state-machine
**Date**: 2026-01-03

## Entity Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Orchestrator Domain                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │  WorkflowState   │───▶│ StateTransition  │    │  AgentConfig   │ │
│  │  (enum)          │    │                  │    │                │ │
│  └──────────────────┘    └──────────────────┘    └────────────────┘ │
│           │                                              │          │
│           ▼                                              ▼          │
│  ┌──────────────────┐                         ┌──────────────────┐  │
│  │ OrchestratorState│                         │   AgentRunner    │  │
│  │ (persisted)      │                         │   (protocol)     │  │
│  └──────────────────┘                         └──────────────────┘  │
│           │                                              │          │
│           ▼                                              ▼          │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │   PhaseResult    │    │   PollResult     │    │  AgentResult   │ │
│  └──────────────────┘    └──────────────────┘    └────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Entities

### WorkflowState (Enum)

Represents the current phase of the SDLC workflow.

```python
class WorkflowState(str, Enum):
    """Workflow states for the orchestrator state machine."""
    IDLE = "idle"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    GATE_1 = "gate_1"
    DONE = "done"
```

**State Transition Graph**:
```
IDLE ──▶ PHASE_1 ──▶ PHASE_2 ──▶ GATE_1 ──▶ DONE
                         ▲          │
                         │          │
                    (polling)  (approval)
```

**Validation Rules**:
- Only forward transitions allowed (no backwards)
- DONE is terminal (no transitions out)
- Invalid transitions raise `InvalidStateTransition`

---

### OrchestratorState (Persisted Entity)

The complete workflow state, persisted to `.plans/{issue}/state.json`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| issue_number | int | Yes | GitHub issue number (primary key) |
| current_state | WorkflowState | Yes | Current workflow state |
| feature_name | str | Yes | Feature slug (e.g., "add-auth") |
| branch_name | str | No | Created branch name (after Phase 1) |
| worktree_path | Path | No | Worktree path (after Phase 1) |
| phase1_steps | list[str] | Yes | Completed Phase 1 steps |
| phase2_agent_complete | bool | Yes | Agent posted ✅ signal |
| phase2_human_approved | bool | Yes | Human posted "approved" |
| history | list[StateTransition] | Yes | Transition history |
| created_at | datetime | Yes | Workflow start time |
| updated_at | datetime | Yes | Last state change |

**Validation Rules**:
- `issue_number` must be positive integer
- `feature_name` must be kebab-case, non-empty
- `phase1_steps` subset of ["issue", "branch", "worktree", "plans"]
- `history` is append-only (immutable entries)

---

### StateTransition (Immutable Record)

Records a single state change event.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| from_state | WorkflowState | Yes | State before transition |
| to_state | WorkflowState | Yes | State after transition |
| trigger | str | Yes | What caused the transition |
| timestamp | datetime | Yes | When transition occurred |

**Validation Rules**:
- `from_state` != `to_state`
- `timestamp` must be UTC
- Record is immutable after creation

---

## Agent Configuration Entities

### AgentProvider (Enum)

Supported AI agent providers.

```python
class AgentProvider(str, Enum):
    """AI agent providers."""
    CLAUDE = "claude"
    GEMINI = "gemini"  # Future
    CODEX = "codex"    # Future
```

### ExecutionMode (Enum)

How the agent is executed.

```python
class ExecutionMode(str, Enum):
    """Agent execution modes."""
    CLI = "cli"   # Command-line interface
    SDK = "sdk"   # SDK/API call (future)
```

### AgentConfig (Configuration Entity)

Complete configuration for dispatching an AI agent.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| provider | AgentProvider | Yes | - | AI provider (claude/gemini/codex) |
| mode | ExecutionMode | Yes | CLI | Execution mode (cli/sdk) |
| model | str | Yes | - | Model name (sonnet/opus/haiku) |
| role | str | Yes | - | Agent role/persona (e.g., "@duc") |
| prompt | str | No | None | Base prompt or skill to invoke |
| skills | list[str] | No | [] | Skills to bundle |
| plugins | list[str] | No | [] | Plugins to include |
| mcp_servers | list[str] | No | [] | MCP servers to configure |
| timeout_seconds | int | No | 3600 | Max execution time |
| work_dir | Path | No | None | Working directory for agent |

**Validation Rules**:
- `model` must be valid for the provider
- `timeout_seconds` must be positive
- At least one of `prompt` or `skills` must be provided

---

### AgentRunner (Protocol)

Interface for executing AI agents.

```python
class AgentRunner(Protocol):
    """Protocol for AI agent execution."""

    def dispatch(self, config: AgentConfig, context: dict[str, Any]) -> AgentResult:
        """Execute an AI agent with the given configuration."""
        ...

    def is_available(self) -> bool:
        """Check if this runner is available on the system."""
        ...

    def get_capabilities(self) -> list[str]:
        """List capabilities this runner supports."""
        ...
```

**Implementations**:
- `ClaudeCLIRunner` - Implemented in this feature
- `ClaudeSDKRunner` - Future (cloud deployment)
- `GeminiCLIRunner` - Future (Gemini support)
- `CodexCLIRunner` - Future (Codex support)

---

### AgentResult (Response Entity)

Result from executing an AI agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | bool | Yes | Whether execution succeeded |
| exit_code | int | No | Process exit code (CLI mode) |
| stdout | str | No | Captured standard output |
| stderr | str | No | Captured standard error |
| duration_seconds | float | No | Execution duration |
| error_message | str | No | Error details if failed |

---

## Phase Execution Entities

### Phase1Request (Request Entity)

Request to start Phase 1 execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| feature_description | str | Yes | Natural language feature description |
| feature_name | str | No | Optional feature slug (derived if not provided) |
| labels | list[str] | No | Additional labels to apply |

**Validation Rules**:
- `feature_description` must be non-empty
- `feature_name` if provided must be kebab-case

---

### Phase2Config (Configuration Entity)

Configuration for Phase 2 execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agent_config | AgentConfig | Yes | Agent to dispatch |
| poll_interval_seconds | int | No | Polling interval (default 30) |
| poll_timeout_seconds | int | No | Total timeout (default 3600) |

---

### PhaseResult (Response Entity)

Result from phase execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | bool | Yes | Whether phase completed successfully |
| phase | str | Yes | Which phase ("phase_1" or "phase_2") |
| artifacts_created | list[str] | No | List of created artifacts |
| steps_completed | list[str] | No | Completed steps |
| error | str | No | Error message if failed |
| duration_seconds | float | No | Execution duration |

---

## Polling Entities

### SignalType (Enum)

Types of signals to poll for.

```python
class SignalType(str, Enum):
    """Types of completion signals."""
    AGENT_COMPLETE = "agent_complete"  # ✅ in comment
    HUMAN_APPROVAL = "human_approval"  # "approved" in comment
```

### PollResult (Response Entity)

Result from polling for a signal.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| detected | bool | Yes | Whether signal was found |
| signal_type | SignalType | Yes | Type of signal polled for |
| comment_id | int | No | ID of matching comment |
| comment_body | str | No | Body of matching comment |
| comment_author | str | No | Author of matching comment |
| poll_count | int | Yes | Number of polls performed |

---

## Label Mapping

| State | Label | Color |
|-------|-------|-------|
| IDLE | `status:new` | #0052cc (blue) |
| PHASE_1 | `status:phase-1` | #fbca04 (yellow) |
| PHASE_2 | `status:phase-2` | #f9a825 (orange) |
| GATE_1 | `status:awaiting-approval` | #7057ff (purple) |
| DONE | `status:done` | #0e8a16 (green) |

---

## Persistence Format

State is persisted as JSON in `.plans/{issue_number}/state.json`:

```json
{
  "issue_number": 123,
  "current_state": "phase_2",
  "feature_name": "add-auth",
  "branch_name": "123-add-auth",
  "worktree_path": "/path/to/repo-123-add-auth",
  "phase1_steps": ["issue", "branch", "worktree", "plans"],
  "phase2_agent_complete": true,
  "phase2_human_approved": false,
  "history": [
    {
      "from_state": "idle",
      "to_state": "phase_1",
      "trigger": "phase_1_start",
      "timestamp": "2026-01-03T10:00:00Z"
    },
    {
      "from_state": "phase_1",
      "to_state": "phase_2",
      "trigger": "phase_1_complete",
      "timestamp": "2026-01-03T10:00:30Z"
    }
  ],
  "created_at": "2026-01-03T10:00:00Z",
  "updated_at": "2026-01-03T10:05:00Z"
}
```
