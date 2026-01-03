# Feature Specification: Orchestrator State Machine

**Feature Branch**: `003-orchestrator-state-machine`
**Created**: 2026-01-03
**Status**: Draft
**Input**: User description: "Feature 1.3: Orchestrator State Machine (Phases 1-2 Only) - State machine that orchestrates SDLC Phase 1 (Issue Setup) and Phase 2 (Specs). Capabilities: State transitions IDLE → PHASE_1 → PHASE_2 → GATE_1 → DONE. Execute Phase 1: Create issue, branch, worktree, .plans structure. Execute Phase 2: Dispatch agent (e.g., @duc). Poll for completion signal (✅ comment from agent). Wait for human approval (approved comment). Update GitHub labels for each state transition. IMPORTANT ARCHITECTURE: The agent spawning must be flexible - use an AgentRunner interface/protocol that can be implemented by different runners (ClaudeCLIRunner now, ClaudeSDKRunner/GeminiCLIRunner/CodexCLIRunner in future). AgentConfig should support: execution mode (cli/sdk), provider (claude/gemini/codex), model (sonnet/opus/etc), role/prompt, and artifacts (skills, plugins, MCP servers). For now only implement ClaudeCLIRunner but design for extensibility."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - State Machine Core (Priority: P1)

A developer wants to track the workflow state of a feature through its lifecycle phases, with clear state transitions and persistence.

**Why this priority**: The state machine is the foundation of the orchestrator. Without state management, no other functionality can operate correctly. This is the core domain model.

**Independent Test**: Can be fully tested by initializing a state machine, transitioning through states, and verifying state persistence and retrieval. Delivers value as a standalone workflow tracker.

**Acceptance Scenarios**:

1. **Given** no existing workflow, **When** the orchestrator initializes, **Then** the state is IDLE
2. **Given** state is IDLE, **When** Phase 1 begins, **Then** state transitions to PHASE_1 and change is persisted
3. **Given** state is PHASE_1, **When** Phase 1 completes, **Then** state transitions to PHASE_2
4. **Given** state is PHASE_2, **When** Phase 2 completes with agent signal, **Then** state transitions to GATE_1
5. **Given** state is GATE_1, **When** human approves, **Then** state transitions to DONE
6. **Given** any state, **When** queried, **Then** current state and history are returned
7. **Given** invalid transition requested, **When** transition attempted, **Then** error is raised with allowed transitions

---

### User Story 2 - Phase 1 Execution (Priority: P2)

A developer wants Phase 1 to automatically create all infrastructure for a new feature: GitHub issue, branch, worktree, and .plans directory structure.

**Why this priority**: Phase 1 execution uses the state machine from US1 and orchestrates existing services (GitHub integration, Worktree Manager). This is the first integration layer.

**Independent Test**: Can be fully tested by triggering Phase 1 and verifying that issue, branch, worktree, and .plans structure are created correctly. Delivers automated feature setup.

**Acceptance Scenarios**:

1. **Given** state is IDLE, **When** Phase 1 is triggered with feature description, **Then** GitHub issue is created
2. **Given** issue is created, **When** Phase 1 continues, **Then** branch named `{issue_number}-{feature_slug}` is created
3. **Given** branch is created, **When** Phase 1 continues, **Then** worktree is created at correct path
4. **Given** worktree is created, **When** Phase 1 continues, **Then** .plans directory structure is initialized
5. **Given** all Phase 1 steps complete, **When** Phase 1 finishes, **Then** state transitions to PHASE_2
6. **Given** any Phase 1 step fails, **When** error occurs, **Then** state remains unchanged and error is reported
7. **Given** Phase 1 triggers, **When** each step completes, **Then** GitHub label is updated to reflect progress

---

### User Story 3 - Agent Dispatch with Flexible Architecture (Priority: P3)

A developer wants to dispatch AI agents with a flexible architecture that supports different providers (Claude, Gemini, Codex), execution modes (CLI, SDK), and configurations.

**Why this priority**: Agent dispatch is the automation engine. The flexible architecture ensures the system can evolve to support multiple AI providers without rewriting core logic. This is strategic extensibility.

**Independent Test**: Can be fully tested by configuring different agent runners and verifying correct dispatch behavior. Delivers AI-powered automation capability.

**Acceptance Scenarios**:

1. **Given** an AgentConfig, **When** agent is dispatched, **Then** the correct runner executes based on provider and mode
2. **Given** ClaudeCLIRunner is configured, **When** agent runs, **Then** Claude CLI is invoked with correct parameters
3. **Given** agent config includes skills, **When** agent runs, **Then** skills are bundled with the invocation
4. **Given** agent config includes plugins, **When** agent runs, **Then** plugins are included in the command
5. **Given** agent config includes MCP servers, **When** agent runs, **Then** MCP servers are configured
6. **Given** agent config specifies model, **When** agent runs, **Then** correct model (sonnet/opus) is used
7. **Given** agent dispatch fails, **When** error occurs, **Then** failure is captured and reported

---

### User Story 4 - Phase 2 Execution with Agent Polling (Priority: P4)

A developer wants Phase 2 to dispatch an architecture agent (@duc) and poll for the completion signal (✅ comment) on the GitHub issue.

**Why this priority**: Phase 2 ties together agent dispatch (US3) and completion detection. This completes the automated specification workflow.

**Independent Test**: Can be fully tested by triggering Phase 2, verifying agent dispatch, and simulating completion signals. Delivers automated specification generation.

**Acceptance Scenarios**:

1. **Given** state is PHASE_2, **When** Phase 2 begins, **Then** architecture agent is dispatched with issue context
2. **Given** agent is running, **When** polling begins, **Then** issue comments are checked periodically
3. **Given** agent posts ✅ comment, **When** poll detects signal, **Then** Phase 2 marks as agent-complete
4. **Given** Phase 2 agent-complete, **When** human posts "approved" comment, **Then** state transitions to GATE_1
5. **Given** polling timeout, **When** no signal received, **Then** state remains PHASE_2 and timeout is reported
6. **Given** Phase 2 progress, **When** milestones reached, **Then** GitHub labels are updated

---

### User Story 5 - GitHub Label State Synchronization (Priority: P5)

A developer wants GitHub issue labels to reflect the current workflow state, enabling visibility and filtering of features by stage.

**Why this priority**: Label synchronization is the communication layer. It makes workflow state visible in GitHub without requiring CLI access.

**Independent Test**: Can be fully tested by triggering state changes and verifying correct labels are applied/removed. Delivers workflow visibility in GitHub.

**Acceptance Scenarios**:

1. **Given** state transitions to PHASE_1, **When** label sync runs, **Then** label `status:phase-1` is applied
2. **Given** state transitions to PHASE_2, **When** label sync runs, **Then** `status:phase-1` is removed and `status:phase-2` is applied
3. **Given** state transitions to GATE_1, **When** label sync runs, **Then** `status:awaiting-approval` is applied
4. **Given** state transitions to DONE, **When** label sync runs, **Then** `status:done` is applied
5. **Given** label sync fails, **When** GitHub API error, **Then** state machine continues and failure is logged

---

### Edge Cases

- What happens when Phase 1 is triggered but the issue already exists? (Resume from last successful step)
- What happens when worktree creation fails due to existing directory? (Report error with remediation steps)
- What happens when agent dispatch fails due to missing CLI? (Clear error with installation instructions)
- What happens when polling finds multiple ✅ comments? (Use first occurrence, log duplicate detection)
- What happens when human approval comes before agent completes? (Ignore premature approval, continue polling)
- What happens when state file is corrupted or missing? (Initialize to IDLE with warning)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a state machine with states: IDLE, PHASE_1, PHASE_2, GATE_1, DONE
- **FR-002**: System MUST persist state changes to disk (JSON file in .plans directory)
- **FR-003**: System MUST validate state transitions against allowed transition graph
- **FR-004**: System MUST execute Phase 1 steps: create issue, create branch, create worktree, initialize .plans
- **FR-005**: System MUST dispatch AI agents using a pluggable runner architecture
- **FR-006**: System MUST support AgentConfig with: provider, mode, model, role, artifacts
- **FR-007**: System MUST implement ClaudeCLIRunner for Claude CLI invocation
- **FR-008**: System MUST poll GitHub comments for agent completion signal (✅)
- **FR-009**: System MUST poll GitHub comments for human approval ("approved")
- **FR-010**: System MUST synchronize GitHub labels with workflow state
- **FR-011**: System MUST provide clear error messages for all failure scenarios
- **FR-012**: System MUST support resumable execution (restart from last successful step)

### Key Entities

- **OrchestratorState**: Represents the current workflow state (IDLE, PHASE_1, PHASE_2, GATE_1, DONE) with timestamps
- **StateTransition**: Records a state change with from_state, to_state, timestamp, and trigger
- **AgentConfig**: Configuration for an AI agent including provider, mode, model, role, prompt, and artifacts
- **AgentRunner**: Protocol/interface for executing agents (ClaudeCLIRunner, future: ClaudeSDKRunner, GeminiCLIRunner)
- **PhaseResult**: Outcome of a phase execution including success status, artifacts created, and errors
- **PollResult**: Result of polling for signals including signal_type, detected, and comment details

### Service Interface

**Service**: OrchestratorService

| Method | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `get_state()` | Get current workflow state | issue_number | OrchestratorState |
| `transition(event)` | Transition to next state | issue_number, event | StateTransition |
| `execute_phase_1(request)` | Run Phase 1 automation | Phase1Request | PhaseResult |
| `execute_phase_2(config)` | Run Phase 2 with agent | Phase2Config | PhaseResult |
| `poll_for_signal(type)` | Poll for completion signal | issue_number, signal_type | PollResult |
| `sync_labels()` | Sync GitHub labels with state | issue_number | OperationResult |

**Service**: AgentRunner (Protocol)

| Method | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `dispatch(config, context)` | Execute an AI agent | AgentConfig, context dict | AgentResult |
| `is_available()` | Check if runner is available | none | bool |
| `get_capabilities()` | List supported features | none | list of capabilities |

**Error Conditions**:
- `InvalidStateTransition`: Transition not allowed from current state
- `Phase1Error`: Phase 1 step failed (with specific sub-error)
- `AgentDispatchError`: Agent failed to launch
- `PollTimeoutError`: No signal detected within timeout
- `LabelSyncError`: GitHub label update failed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: State machine can complete full workflow (IDLE → DONE) in under 5 minutes with mocked agents
- **SC-002**: Phase 1 creates all artifacts (issue, branch, worktree, .plans) in under 30 seconds
- **SC-003**: Agent dispatch completes within 5 seconds of triggering
- **SC-004**: Polling detects completion signal within one poll cycle (configurable, default 30s)
- **SC-005**: Label synchronization completes within 2 seconds of state change
- **SC-006**: System recovers from interrupted execution by resuming from last successful step
- **SC-007**: Error messages include actionable remediation steps for 100% of failure scenarios

## Assumptions

- GitHub integration (Feature 001) is complete and available for use
- Worktree Manager (Feature 002) is complete and available for use
- Claude CLI is installed and configured on developer machines
- GitHub App has permissions for issues, labels, and comments
- .plans directory structure follows existing convention from worktree manager
- Polling interval is configurable with sensible defaults (30 seconds)
- State persistence uses JSON for simplicity (upgrade to SQLite later if needed)

## Architecture Notes

### AgentRunner Protocol Design

The agent spawning architecture must be flexible to support future providers:

```
AgentRunner (Protocol)
├── ClaudeCLIRunner (Implemented in this feature)
├── ClaudeSDKRunner (Future: for cloud deployment)
├── GeminiCLIRunner (Future: for Gemini support)
└── CodexCLIRunner (Future: for Codex support)
```

**AgentConfig Structure**:
- `provider`: "claude" | "gemini" | "codex"
- `mode`: "cli" | "sdk"
- `model`: "sonnet" | "opus" | "haiku" | "pro" | "flash" etc.
- `role`: Agent role/persona (e.g., "@duc" for architect)
- `prompt`: Base prompt or skill to invoke
- `artifacts`: List of skills, plugins, or MCP servers to bundle

**ClaudeCLIRunner Implementation**:
- Invokes `claude` CLI with appropriate flags
- Passes `--model` for model selection
- Handles skill bundling via CLI arguments
- Captures output and exit codes
- Supports background execution for long-running tasks

This design allows adding new runners (GeminiCLIRunner, CodexCLIRunner) without modifying core orchestrator logic.
