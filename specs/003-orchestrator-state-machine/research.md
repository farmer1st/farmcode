# Research: Orchestrator State Machine

**Feature**: 003-orchestrator-state-machine
**Date**: 2026-01-03
**Status**: Complete

## Research Tasks

### R1: State Machine Implementation Pattern

**Question**: How to implement a robust state machine in Python?

**Decision**: Use a simple dictionary-based transition table with Pydantic models for state.

**Rationale**:
- Python's enum and dataclasses/Pydantic provide type-safe state representation
- Dictionary-based transition tables are simple and explicit
- No external library needed (like `transitions`) - follows YAGNI principle
- Pattern matches existing codebase style (github_integration, worktree_manager)

**Alternatives Considered**:
- `transitions` library: Adds dependency, more complex than needed
- Class-based state pattern: Over-engineered for 5 states
- Async state machine: Not needed for CLI tool

**Implementation**:
```python
TRANSITIONS = {
    WorkflowState.IDLE: [WorkflowState.PHASE_1],
    WorkflowState.PHASE_1: [WorkflowState.PHASE_2],
    WorkflowState.PHASE_2: [WorkflowState.GATE_1],
    WorkflowState.GATE_1: [WorkflowState.DONE],
    WorkflowState.DONE: [],  # Terminal state
}
```

---

### R2: State Persistence Strategy

**Question**: How to persist workflow state between CLI invocations?

**Decision**: JSON file in `.plans/{issue_number}/state.json` within the worktree.

**Rationale**:
- JSON is human-readable and debuggable
- Consistent with .plans directory convention from worktree manager
- File-per-issue allows multiple workflows in parallel
- Easy to reset (delete file)
- No database setup required (local-first)

**Alternatives Considered**:
- SQLite: Over-engineered for single-value state storage
- YAML: Less standard for data, JSON preferred
- Environment variable: Doesn't persist across sessions
- Central state file: Complicates parallel workflows

**Implementation**:
```python
STATE_FILE = ".plans/{issue_number}/state.json"
```

---

### R3: AgentRunner Protocol Design

**Question**: How to design an extensible agent runner interface?

**Decision**: Python Protocol class with three methods: `dispatch()`, `is_available()`, `get_capabilities()`.

**Rationale**:
- Protocol (PEP 544) enables structural subtyping (duck typing with types)
- No inheritance required - any class with matching methods works
- Easy to add GeminiCLIRunner, CodexCLIRunner later
- Matches existing patterns in codebase

**Alternatives Considered**:
- ABC (Abstract Base Class): Requires explicit inheritance, less flexible
- Simple function: Doesn't encapsulate availability/capabilities
- Plugin system: Over-engineered for 2-4 runners

**Implementation**:
```python
class AgentRunner(Protocol):
    def dispatch(self, config: AgentConfig, context: dict) -> AgentResult: ...
    def is_available(self) -> bool: ...
    def get_capabilities(self) -> list[str]: ...
```

---

### R4: Claude CLI Invocation

**Question**: How to invoke Claude CLI from Python?

**Decision**: Use `subprocess.run()` with proper argument handling.

**Rationale**:
- subprocess is stdlib, no additional dependencies
- Sync execution is fine for CLI tool
- Can capture stdout/stderr for logging
- Supports background execution via Popen if needed

**Alternatives Considered**:
- os.system(): Less control, security concerns
- asyncio.subprocess: Async not needed for CLI
- Shell scripts: Less portable, harder to test

**Key CLI Flags** (from Claude CLI docs):
- `--model sonnet|opus|haiku` - Model selection
- `--prompt "..."` - Initial prompt
- `--print` - Output only, no interactive
- `-p "..."` - Alternative prompt flag

**Implementation**:
```python
cmd = ["claude", "--model", config.model, "--print", "-p", config.prompt]
result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
```

---

### R5: Comment Polling Strategy

**Question**: How to poll for completion signals in GitHub comments?

**Decision**: Periodic polling with configurable interval, using existing GitHubService.

**Rationale**:
- GitHub doesn't support webhooks for local CLI
- Polling is simple and reliable
- Reuses existing GitHubService.list_comments()
- Interval configurable (default 30s)

**Alternatives Considered**:
- Webhooks: Requires public endpoint, not for local CLI
- GitHub Actions workflow_dispatch: Different use case
- Manual refresh: Poor UX

**Signal Detection**:
- Agent completion: Comment contains "✅" emoji
- Human approval: Comment contains "approved" (case-insensitive)
- First matching comment wins (chronological)

**Implementation**:
```python
def poll_for_signal(self, issue_number: int, signal_type: SignalType) -> PollResult:
    comments = self.github.list_comments(issue_number)
    for comment in comments:
        if self._matches_signal(comment.body, signal_type):
            return PollResult(detected=True, comment=comment)
    return PollResult(detected=False)
```

---

### R6: Label Naming Convention

**Question**: What labels to use for workflow state?

**Decision**: Use `status:` prefix with kebab-case state names.

**Rationale**:
- Prefix enables filtering (all status labels)
- Kebab-case is GitHub convention
- Matches existing label patterns in codebase

**Label Mapping**:
| State | Label |
|-------|-------|
| IDLE | `status:new` |
| PHASE_1 | `status:phase-1` |
| PHASE_2 | `status:phase-2` |
| GATE_1 | `status:awaiting-approval` |
| DONE | `status:done` |

**Implementation**:
- Remove previous status label before adding new one
- Create label if it doesn't exist (idempotent)

---

### R7: Error Recovery Strategy

**Question**: How to handle failures and enable resumption?

**Decision**: Track step completion in state file, resume from last successful step.

**Rationale**:
- Each Phase 1 step is atomic and idempotent
- State file tracks which steps completed
- On restart, skip completed steps
- Simple and predictable

**Implementation**:
```python
class WorkflowState(BaseModel):
    current_state: StateEnum
    phase1_steps_completed: list[str]  # ["issue", "branch", "worktree", "plans"]
    phase2_agent_complete: bool
    phase2_human_approved: bool
```

---

## Dependencies Identified

| Dependency | Purpose | Already Available |
|------------|---------|-------------------|
| github_integration | GitHub API (issues, comments, labels) | Yes (Feature 001) |
| worktree_manager | Worktree creation | Yes (Feature 002) |
| subprocess | CLI invocation | Yes (stdlib) |
| pydantic | Models and validation | Yes (existing) |

## Conclusion

All research questions resolved. No external dependencies required beyond existing codebase. Ready for Phase 1 design.
