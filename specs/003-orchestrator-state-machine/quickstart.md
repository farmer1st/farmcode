# Quickstart: Orchestrator State Machine

**Feature**: 003-orchestrator-state-machine
**Date**: 2026-01-03

This guide demonstrates end-to-end usage of the Orchestrator for Phases 1-2.

## Prerequisites

1. **GitHub Integration** configured (Feature 001)
   - GitHub App credentials in `.env`
   - Repository access configured

2. **Worktree Manager** available (Feature 002)
   - Git repository initialized
   - Main branch set up

3. **Claude CLI** installed (for agent dispatch)
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude --version
   ```

## Scenario 1: Start a New Feature (Phase 1)

Create a new feature workflow with issue, branch, worktree, and .plans structure.

### Code

```python
from pathlib import Path
from github_integration import GitHubService
from worktree_manager import WorktreeService
from orchestrator import OrchestratorService, Phase1Request

# Initialize services
github = GitHubService.from_env()
worktree = WorktreeService(Path("."))
orchestrator = OrchestratorService(Path("."), github, worktree)

# Start Phase 1
result = orchestrator.execute_phase_1(
    Phase1Request(
        feature_description="Add OAuth2 authentication with Google login",
        labels=["enhancement", "security"],
    )
)

print(f"Success: {result.success}")
print(f"Artifacts: {result.artifacts_created}")
print(f"Steps: {result.steps_completed}")
```

### Expected Output

```
Success: True
Artifacts: ['issue#123', 'branch:123-oauth2-auth', 'worktree:/path/to/repo-123-oauth2-auth', '.plans/123/']
Steps: ['issue', 'branch', 'worktree', 'plans']
```

### Verification

```bash
# Check GitHub issue exists
gh issue view 123

# Check branch exists
git branch -a | grep 123-oauth2-auth

# Check worktree exists
ls -la ../repo-123-oauth2-auth

# Check .plans structure
ls -la ../repo-123-oauth2-auth/.plans/123/
```

---

## Scenario 2: Check Workflow State

Query the current state of a workflow.

### Code

```python
# Get current state
state = orchestrator.get_state(123)

if state:
    print(f"Current state: {state.current_state}")
    print(f"Feature: {state.feature_name}")
    print(f"Phase 1 complete: {len(state.phase1_steps) == 4}")
    print(f"Transition history: {len(state.history)} events")
else:
    print("No workflow found for issue 123")
```

### Expected Output

```
Current state: WorkflowState.PHASE_2
Feature: oauth2-auth
Phase 1 complete: True
Transition history: 2 events
```

---

## Scenario 3: Dispatch Agent (Phase 2)

Dispatch an AI agent to work on the specification.

### Code

```python
from orchestrator import Phase2Config, AgentConfig, AgentProvider, ExecutionMode

# Configure agent
agent_config = AgentConfig(
    provider=AgentProvider.CLAUDE,
    mode=ExecutionMode.CLI,
    model="sonnet",
    role="@duc",
    prompt="Design the OAuth2 authentication system architecture",
    skills=["/speckit.specify"],
)

# Execute Phase 2
result = orchestrator.execute_phase_2(
    issue_number=123,
    config=Phase2Config(
        agent_config=agent_config,
        poll_interval_seconds=30,
        poll_timeout_seconds=3600,
    ),
)

print(f"Success: {result.success}")
print(f"Duration: {result.duration_seconds:.1f}s")
```

### Expected Output

```
Success: True
Duration: 245.3s
```

---

## Scenario 4: Poll for Signal Manually

Poll for completion signals without executing the full phase.

### Code

```python
from orchestrator import SignalType

# Poll for agent completion
agent_result = orchestrator.poll_for_signal(
    issue_number=123,
    signal_type=SignalType.AGENT_COMPLETE,
    timeout_seconds=60,
    interval_seconds=10,
)

print(f"Agent complete: {agent_result.detected}")
if agent_result.detected:
    print(f"Signal from: {agent_result.comment_author}")

# Poll for human approval
approval_result = orchestrator.poll_for_signal(
    issue_number=123,
    signal_type=SignalType.HUMAN_APPROVAL,
    timeout_seconds=60,
    interval_seconds=10,
)

print(f"Human approved: {approval_result.detected}")
```

### Expected Output

```
Agent complete: True
Signal from: github-actions[bot]
Human approved: False
```

---

## Scenario 5: Sync Labels Manually

Synchronize GitHub labels with current workflow state.

### Code

```python
# Sync labels
result = orchestrator.sync_labels(123)

print(f"Success: {result.status}")
```

### Expected Output

```
Success: OperationStatus.SUCCESS
```

### Verification

```bash
# Check labels on issue
gh issue view 123 --json labels
```

Expected labels include `status:phase-2` or appropriate state label.

---

## Scenario 6: Resume After Failure

Resume a workflow that was interrupted.

### Code

```python
# Get current state
state = orchestrator.get_state(123)

if state and state.current_state == WorkflowState.PHASE_1:
    # Check what steps are missing
    missing = set(["issue", "branch", "worktree", "plans"]) - set(state.phase1_steps)
    print(f"Missing steps: {missing}")

    # Resume Phase 1 (will skip completed steps)
    result = orchestrator.execute_phase_1(
        Phase1Request(
            feature_description="Add OAuth2 authentication",
        )
    )
    print(f"Resumed and completed: {result.success}")
```

### Expected Output

```
Missing steps: {'worktree', 'plans'}
Resumed and completed: True
```

---

## Scenario 7: Check Agent Availability

Verify agent runner is available before dispatch.

### Code

```python
from orchestrator.agent_runner import ClaudeCLIRunner, get_runner

# Check Claude CLI directly
runner = ClaudeCLIRunner()
print(f"Claude CLI available: {runner.is_available()}")
print(f"Capabilities: {runner.get_capabilities()}")

# Via factory function
try:
    runner = get_runner(AgentConfig(
        provider=AgentProvider.CLAUDE,
        mode=ExecutionMode.CLI,
        model="sonnet",
        role="test",
        prompt="test",
    ))
    print("Runner obtained successfully")
except AgentNotAvailableError as e:
    print(f"Runner not available: {e.message}")
```

### Expected Output

```
Claude CLI available: True
Capabilities: ['skills', 'plugins', 'mcp', 'model_selection']
Runner obtained successfully
```

---

## Error Handling Examples

### Invalid State Transition

```python
from orchestrator.errors import InvalidStateTransition

try:
    # Try to go backwards (not allowed)
    orchestrator.transition(123, "phase_1_start")  # Already in PHASE_2
except InvalidStateTransition as e:
    print(f"Error: {e.message}")
    print(f"Error code: {e.error_code}")
```

Output:
```
Error: Cannot transition from PHASE_2 to PHASE_1
Error code: INVALID_TRANSITION
```

### Workflow Not Found

```python
from orchestrator.errors import WorkflowNotFoundError

try:
    state = orchestrator.get_state(999)
    if state is None:
        print("No workflow for issue 999")
except WorkflowNotFoundError as e:
    print(f"Error: {e.message}")
```

Output:
```
No workflow for issue 999
```

### Agent Not Available

```python
from orchestrator.errors import AgentNotAvailableError

try:
    result = orchestrator.execute_phase_2(
        123,
        Phase2Config(
            agent_config=AgentConfig(
                provider=AgentProvider.GEMINI,  # Not implemented
                mode=ExecutionMode.CLI,
                model="pro",
                role="test",
                prompt="test",
            ),
        ),
    )
except AgentNotAvailableError as e:
    print(f"Error: {e.message}")
    print(f"Error code: {e.error_code}")
```

Output:
```
Error: Provider gemini not yet implemented
Error code: AGENT_NOT_AVAILABLE
```

---

## State File Location

Workflow state is persisted at:
```
{worktree_path}/.plans/{issue_number}/state.json
```

Example:
```bash
cat ../repo-123-oauth2-auth/.plans/123/state.json
```

```json
{
  "issue_number": 123,
  "current_state": "phase_2",
  "feature_name": "oauth2-auth",
  "branch_name": "123-oauth2-auth",
  "worktree_path": "/path/to/repo-123-oauth2-auth",
  "phase1_steps": ["issue", "branch", "worktree", "plans"],
  "phase2_agent_complete": false,
  "phase2_human_approved": false,
  "history": [...],
  "created_at": "2026-01-03T10:00:00Z",
  "updated_at": "2026-01-03T10:00:30Z"
}
```
