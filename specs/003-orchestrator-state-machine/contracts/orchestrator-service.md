# Contract: OrchestratorService

**Module**: `src/orchestrator/service.py`
**Type**: Python Service Class

## Overview

The OrchestratorService is the main facade for the orchestrator module. It coordinates state management, phase execution, signal polling, and label synchronization.

## Service Interface

### Constructor

```python
class OrchestratorService:
    def __init__(
        self,
        repo_path: Path,
        github_service: GitHubService,
        worktree_service: WorktreeService,
        agent_runner: AgentRunner | None = None,
    ) -> None:
        """Initialize the orchestrator service.

        Args:
            repo_path: Path to the main git repository.
            github_service: GitHub service for API operations.
            worktree_service: Worktree service for worktree operations.
            agent_runner: Agent runner (defaults to ClaudeCLIRunner).

        Raises:
            NotARepositoryError: If repo_path is not a git repository.
        """
```

---

## State Management Methods

### get_state

```python
def get_state(self, issue_number: int) -> OrchestratorState | None:
    """Get current workflow state for an issue.

    Args:
        issue_number: GitHub issue number.

    Returns:
        Current OrchestratorState or None if no workflow exists.

    Raises:
        StateFileCorruptedError: If state file is malformed.
    """
```

**Example**:
```python
service = OrchestratorService(repo_path, github, worktree)
state = service.get_state(123)
if state:
    print(f"Current state: {state.current_state}")
else:
    print("No workflow found for issue 123")
```

---

### transition

```python
def transition(
    self,
    issue_number: int,
    event: str,
) -> StateTransition:
    """Transition workflow to next state.

    Args:
        issue_number: GitHub issue number.
        event: Event triggering the transition.

    Returns:
        StateTransition record of the change.

    Raises:
        WorkflowNotFoundError: If no workflow exists for issue.
        InvalidStateTransition: If transition not allowed.
    """
```

**Events**:
| Event | From State | To State |
|-------|------------|----------|
| `phase_1_start` | IDLE | PHASE_1 |
| `phase_1_complete` | PHASE_1 | PHASE_2 |
| `phase_2_complete` | PHASE_2 | GATE_1 |
| `approval_received` | GATE_1 | DONE |

---

## Phase Execution Methods

### execute_phase_1

```python
def execute_phase_1(
    self,
    request: Phase1Request,
) -> PhaseResult:
    """Execute Phase 1: Issue Setup.

    Creates GitHub issue, branch, worktree, and .plans structure.

    Args:
        request: Phase 1 configuration.

    Returns:
        PhaseResult with created artifacts.

    Raises:
        WorkflowAlreadyExistsError: If workflow already in progress.
        IssueCreationError: If GitHub issue creation fails.
        BranchExistsError: If branch already exists.
        WorktreeExistsError: If worktree path exists.
    """
```

**Example**:
```python
result = service.execute_phase_1(
    Phase1Request(
        feature_description="Add user authentication",
        labels=["enhancement", "priority:high"],
    )
)
if result.success:
    print(f"Created issue #{result.artifacts_created}")
```

**Steps Performed**:
1. Create GitHub issue with description
2. Create branch `{issue_number}-{feature_slug}`
3. Create worktree at `{repo}-{issue_number}-{feature_slug}`
4. Initialize `.plans/{issue_number}/` directory structure
5. Apply `status:phase-1` label
6. Transition state IDLE → PHASE_1 → PHASE_2

---

### execute_phase_2

```python
def execute_phase_2(
    self,
    issue_number: int,
    config: Phase2Config,
) -> PhaseResult:
    """Execute Phase 2: Specification with Agent.

    Dispatches agent and polls for completion signals.

    Args:
        issue_number: GitHub issue number.
        config: Phase 2 configuration including agent config.

    Returns:
        PhaseResult indicating outcome.

    Raises:
        WorkflowNotFoundError: If no workflow for issue.
        InvalidStateError: If not in PHASE_2 state.
        AgentDispatchError: If agent fails to start.
        PollTimeoutError: If signals not received in time.
    """
```

**Steps Performed**:
1. Dispatch agent with issue context
2. Poll for agent completion signal (✅)
3. Update label to `status:awaiting-approval`
4. Poll for human approval ("approved")
5. Transition state PHASE_2 → GATE_1 → DONE

---

## Polling Methods

### poll_for_signal

```python
def poll_for_signal(
    self,
    issue_number: int,
    signal_type: SignalType,
    timeout_seconds: int = 3600,
    interval_seconds: int = 30,
) -> PollResult:
    """Poll for a completion signal in issue comments.

    Args:
        issue_number: GitHub issue number.
        signal_type: Type of signal to poll for.
        timeout_seconds: Maximum time to poll (default 1 hour).
        interval_seconds: Time between polls (default 30s).

    Returns:
        PollResult with detection status.

    Raises:
        PollTimeoutError: If timeout reached without signal.
    """
```

**Signal Detection**:
| SignalType | Pattern |
|------------|---------|
| AGENT_COMPLETE | Comment contains "✅" |
| HUMAN_APPROVAL | Comment contains "approved" (case-insensitive) |

---

## Label Synchronization Methods

### sync_labels

```python
def sync_labels(
    self,
    issue_number: int,
) -> OperationResult:
    """Synchronize GitHub labels with current state.

    Removes old status labels and applies current state label.

    Args:
        issue_number: GitHub issue number.

    Returns:
        OperationResult indicating success/failure.

    Raises:
        WorkflowNotFoundError: If no workflow for issue.
    """
```

**Label Mapping**:
| State | Label |
|-------|-------|
| IDLE | `status:new` |
| PHASE_1 | `status:phase-1` |
| PHASE_2 | `status:phase-2` |
| GATE_1 | `status:awaiting-approval` |
| DONE | `status:done` |

---

## Error Handling

All errors inherit from `OrchestratorError`:

```python
class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class WorkflowNotFoundError(OrchestratorError):
    """No workflow exists for the given issue."""
    error_code = "WORKFLOW_NOT_FOUND"

class WorkflowAlreadyExistsError(OrchestratorError):
    """Workflow already in progress for issue."""
    error_code = "WORKFLOW_EXISTS"

class InvalidStateTransition(OrchestratorError):
    """Requested transition is not allowed."""
    error_code = "INVALID_TRANSITION"

class InvalidStateError(OrchestratorError):
    """Operation not valid for current state."""
    error_code = "INVALID_STATE"

class StateFileCorruptedError(OrchestratorError):
    """State file is malformed or unreadable."""
    error_code = "STATE_CORRUPTED"

class AgentDispatchError(OrchestratorError):
    """Agent failed to dispatch."""
    error_code = "AGENT_DISPATCH_ERROR"

class PollTimeoutError(OrchestratorError):
    """Polling timed out without detecting signal."""
    error_code = "POLL_TIMEOUT"
```

---

## Thread Safety

The OrchestratorService is **not** thread-safe. For concurrent access:
- Use file locking on state.json
- Or run separate instances per issue

---

## Usage Example

```python
from pathlib import Path
from github_integration import GitHubService
from worktree_manager import WorktreeService
from orchestrator import (
    OrchestratorService,
    Phase1Request,
    Phase2Config,
    AgentConfig,
    AgentProvider,
    ExecutionMode,
)

# Initialize services
github = GitHubService.from_env()
worktree = WorktreeService(Path("."))
orchestrator = OrchestratorService(Path("."), github, worktree)

# Execute Phase 1
result = orchestrator.execute_phase_1(
    Phase1Request(
        feature_description="Add OAuth2 authentication",
        labels=["enhancement"],
    )
)
print(f"Created issue #{result.artifacts_created[0]}")

# Execute Phase 2
issue_number = int(result.artifacts_created[0].split("#")[1])
orchestrator.execute_phase_2(
    issue_number,
    Phase2Config(
        agent_config=AgentConfig(
            provider=AgentProvider.CLAUDE,
            mode=ExecutionMode.CLI,
            model="sonnet",
            role="@duc",
            prompt="Design the OAuth2 authentication system",
        ),
        poll_interval_seconds=30,
    ),
)
```
