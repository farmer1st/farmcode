# Tasks: Orchestrator State Machine

**Input**: Design documents from `/specs/003-orchestrator-state-machine/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/orchestrator-service.md, contracts/agent-runner.md

**Tests**: TDD approach - contract and unit tests written before implementation per Constitution Principle I.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/orchestrator/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and module structure

- [X] T001 Create orchestrator module directory structure per plan.md in src/orchestrator/
- [X] T002 Create src/orchestrator/__init__.py with public exports skeleton
- [X] T003 [P] Create src/orchestrator/logger.py with module logger configuration
- [X] T004 [P] Update pyproject.toml to include orchestrator module in coverage settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models and error handling that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create base error classes in src/orchestrator/errors.py (OrchestratorError, error_code pattern)
- [X] T006 [P] Create WorkflowState enum in src/orchestrator/models.py
- [X] T007 [P] Create AgentProvider enum in src/orchestrator/models.py
- [X] T008 [P] Create ExecutionMode enum in src/orchestrator/models.py
- [X] T009 [P] Create SignalType enum in src/orchestrator/models.py
- [X] T010 Create StateTransition model in src/orchestrator/models.py
- [X] T011 Create OrchestratorState model in src/orchestrator/models.py (depends on T006, T010)
- [X] T012 [P] Create AgentConfig model in src/orchestrator/models.py
- [X] T013 [P] Create AgentResult model in src/orchestrator/models.py
- [X] T014 [P] Create Phase1Request model in src/orchestrator/models.py
- [X] T015 [P] Create Phase2Config model in src/orchestrator/models.py
- [X] T016 [P] Create PhaseResult model in src/orchestrator/models.py
- [X] T017 [P] Create PollResult model in src/orchestrator/models.py
- [X] T018 Add all specific error classes to src/orchestrator/errors.py (InvalidStateTransition, WorkflowNotFoundError, etc.)
- [X] T019 Update src/orchestrator/__init__.py with all model and error exports

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - State Machine Core (Priority: P1) 🎯 MVP

**Goal**: Track workflow state through lifecycle phases with persistence and validation

**Independent Test**: Initialize state machine, transition through all states, verify persistence and invalid transition handling

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T020 [P] [US1] Unit test for WorkflowState transitions in tests/unit/test_state_machine.py
- [X] T021 [P] [US1] Unit test for state persistence (save/load) in tests/unit/test_state_machine.py
- [X] T022 [P] [US1] Unit test for invalid transition handling in tests/unit/test_state_machine.py
- [X] T023 [P] [US1] Unit test for state history tracking in tests/unit/test_state_machine.py

### Implementation for User Story 1

- [X] T024 [US1] Implement TRANSITIONS dict with allowed state transitions in src/orchestrator/state_machine.py
- [X] T025 [US1] Implement StateMachine class with get_state() method in src/orchestrator/state_machine.py
- [X] T026 [US1] Implement transition() method with validation in src/orchestrator/state_machine.py
- [X] T027 [US1] Implement state persistence (_save_state, _load_state) in src/orchestrator/state_machine.py
- [X] T028 [US1] Implement state history tracking (append StateTransition) in src/orchestrator/state_machine.py
- [X] T029 [US1] Handle corrupted/missing state file (initialize to IDLE with warning) in src/orchestrator/state_machine.py
- [X] T030 [US1] Add Google-style docstrings to all StateMachine methods

**Checkpoint**: State machine fully functional and testable independently

---

## Phase 4: User Story 2 - Phase 1 Execution (Priority: P2)

**Goal**: Automatically create GitHub issue, branch, worktree, and .plans structure

**Independent Test**: Trigger Phase 1 with feature description, verify all artifacts created correctly

### Tests for User Story 2

- [X] T031 [P] [US2] Integration test for execute_phase_1() in tests/integration/test_orchestrator_integration.py
- [X] T032 [P] [US2] Unit test for Phase 1 step execution in tests/unit/test_phase_executor.py
- [X] T033 [P] [US2] Unit test for resumable execution (skip completed steps) in tests/unit/test_phase_executor.py

### Implementation for User Story 2

- [X] T034 [US2] Create PhaseExecutor class in src/orchestrator/phase_executor.py
- [X] T035 [US2] Implement _create_issue() step using GitHubService in src/orchestrator/phase_executor.py
- [X] T036 [US2] Implement _create_branch() step using GitHubService in src/orchestrator/phase_executor.py
- [X] T037 [US2] Implement _create_worktree() step using WorktreeService in src/orchestrator/phase_executor.py
- [X] T038 [US2] Implement _initialize_plans() step to create .plans/{issue}/ structure in src/orchestrator/phase_executor.py
- [X] T039 [US2] Implement execute_phase_1() orchestrating all steps in src/orchestrator/phase_executor.py
- [X] T040 [US2] Implement step tracking (phase1_steps) for resumable execution in src/orchestrator/phase_executor.py
- [X] T041 [US2] Implement error handling with Phase1Error and sub-errors in src/orchestrator/phase_executor.py
- [X] T042 [US2] Add Google-style docstrings to all PhaseExecutor methods

**Checkpoint**: Phase 1 execution creates all artifacts and integrates with state machine

---

## Phase 5: User Story 3 - Agent Dispatch with Flexible Architecture (Priority: P3)

**Goal**: Dispatch AI agents with pluggable runner architecture supporting multiple providers

**Independent Test**: Configure ClaudeCLIRunner, dispatch agent, verify correct CLI invocation

### Tests for User Story 3

- [X] T043 [P] [US3] Unit test for AgentRunner protocol in tests/unit/test_agent_runner.py
- [X] T044 [P] [US3] Unit test for ClaudeCLIRunner.is_available() in tests/unit/test_agent_runner.py
- [X] T045 [P] [US3] Unit test for ClaudeCLIRunner.dispatch() in tests/unit/test_agent_runner.py
- [X] T046 [P] [US3] Unit test for get_runner() factory in tests/unit/test_agent_runner.py

### Implementation for User Story 3

- [X] T047 [US3] Create AgentRunner Protocol in src/orchestrator/agent_runner.py
- [X] T048 [US3] Implement ClaudeCLIRunner.__init__() with claude_path in src/orchestrator/agent_runner.py
- [X] T049 [US3] Implement ClaudeCLIRunner.is_available() checking claude --version in src/orchestrator/agent_runner.py
- [X] T050 [US3] Implement ClaudeCLIRunner.get_capabilities() returning supported features in src/orchestrator/agent_runner.py
- [X] T051 [US3] Implement ClaudeCLIRunner.dispatch() with subprocess invocation in src/orchestrator/agent_runner.py
- [X] T052 [US3] Implement CLI command construction (model, prompt, skills, plugins, mcp) in src/orchestrator/agent_runner.py
- [X] T053 [US3] Implement get_runner() factory function in src/orchestrator/agent_runner.py
- [X] T054 [US3] Add agent-specific errors (AgentDispatchError, AgentExecutionError, AgentTimeoutError, AgentNotAvailableError) to src/orchestrator/errors.py
- [X] T055 [US3] Add Google-style docstrings to all AgentRunner classes and methods

**Checkpoint**: Agent dispatch works independently with ClaudeCLIRunner

---

## Phase 6: User Story 4 - Phase 2 Execution with Agent Polling (Priority: P4)

**Goal**: Dispatch architecture agent and poll for completion/approval signals

**Independent Test**: Trigger Phase 2, verify agent dispatch, simulate completion signals

### Tests for User Story 4

- [X] T056 [P] [US4] Unit test for poll_for_signal() in tests/unit/test_polling.py
- [X] T057 [P] [US4] Unit test for signal detection (✅ and "approved") in tests/unit/test_polling.py
- [X] T058 [P] [US4] Unit test for poll timeout handling in tests/unit/test_polling.py
- [X] T059 [P] [US4] Integration test for execute_phase_2() in tests/integration/test_orchestrator_integration.py

### Implementation for User Story 4

- [X] T060 [US4] Create SignalPoller class in src/orchestrator/polling.py
- [X] T061 [US4] Implement poll_for_signal() with interval and timeout in src/orchestrator/polling.py
- [X] T062 [US4] Implement _check_for_signal() checking issue comments in src/orchestrator/polling.py
- [X] T063 [US4] Implement signal detection logic (✅ for agent, "approved" for human) in src/orchestrator/polling.py
- [X] T064 [US4] Implement execute_phase_2() in src/orchestrator/phase_executor.py
- [X] T065 [US4] Integrate agent dispatch + polling in execute_phase_2() in src/orchestrator/phase_executor.py
- [X] T066 [US4] Handle poll timeout with PollTimeoutError in src/orchestrator/polling.py
- [X] T067 [US4] Add Google-style docstrings to all SignalPoller methods

**Checkpoint**: Phase 2 execution with agent dispatch and signal polling works

---

## Phase 7: User Story 5 - GitHub Label State Synchronization (Priority: P5)

**Goal**: Synchronize GitHub issue labels with current workflow state

**Independent Test**: Trigger state changes, verify correct labels applied/removed

### Tests for User Story 5

- [X] T068 [P] [US5] Unit test for label mapping in tests/unit/test_label_sync.py
- [X] T069 [P] [US5] Unit test for sync_labels() in tests/unit/test_label_sync.py
- [X] T070 [P] [US5] Unit test for label sync error handling in tests/unit/test_label_sync.py

### Implementation for User Story 5

- [X] T071 [US5] Create LabelSync class in src/orchestrator/label_sync.py
- [X] T072 [US5] Implement STATE_LABEL_MAP constant in src/orchestrator/label_sync.py
- [X] T073 [US5] Implement sync_labels() removing old status labels in src/orchestrator/label_sync.py
- [X] T074 [US5] Implement sync_labels() applying current state label in src/orchestrator/label_sync.py
- [X] T075 [US5] Handle GitHub API errors gracefully (log and continue) in src/orchestrator/label_sync.py
- [X] T076 [US5] Add Google-style docstrings to all LabelSync methods

**Checkpoint**: Label synchronization works independently

---

## Phase 8: Service Integration & E2E

**Purpose**: Integrate all components into OrchestratorService facade

### Tests

- [X] T077 [P] Contract test for OrchestratorService in tests/contract/test_orchestrator_contract.py
- [X] T078 [P] E2E test for full workflow (IDLE → DONE) in tests/e2e/test_orchestrator_e2e.py

### Implementation

- [X] T079 Create OrchestratorService class in src/orchestrator/service.py
- [X] T080 Implement OrchestratorService.__init__() with dependency injection in src/orchestrator/service.py
- [X] T081 Implement get_state() delegating to StateMachine in src/orchestrator/service.py
- [X] T082 Implement transition() delegating to StateMachine in src/orchestrator/service.py
- [X] T083 Implement execute_phase_1() delegating to PhaseExecutor in src/orchestrator/service.py
- [X] T084 Implement execute_phase_2() delegating to PhaseExecutor in src/orchestrator/service.py
- [X] T085 Implement poll_for_signal() delegating to SignalPoller in src/orchestrator/service.py
- [X] T086 Implement sync_labels() delegating to LabelSync in src/orchestrator/service.py
- [X] T087 Wire label sync to state transitions automatically in src/orchestrator/service.py
- [X] T088 Update src/orchestrator/__init__.py with OrchestratorService export
- [X] T089 Add Google-style docstrings to all OrchestratorService methods

**Checkpoint**: OrchestratorService facade complete and tested

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and quality improvements

### User Journey Documentation (REQUIRED per Constitution Principle XI)

- [X] T090 [P] Create docs/user-journeys/ORC-001-track-workflow-state.md (covered by existing ORC-001 through ORC-005)
- [X] T091 [P] Create docs/user-journeys/ORC-002-setup-feature-infrastructure.md (covered by existing ORC-001)
- [X] T092 [P] Create docs/user-journeys/ORC-003-dispatch-ai-agent.md (covered by existing ORC-002)
- [X] T093 [P] Create docs/user-journeys/ORC-004-execute-specification-phase.md (covered by existing ORC-003, ORC-005)
- [X] T094 [P] Create docs/user-journeys/ORC-005-sync-labels-with-state.md (covered by existing ORC-003)
- [X] T095 Update docs/user-journeys/JOURNEYS.md with ORC journeys (already contains ORC journeys)
- [X] T096 Add @pytest.mark.journey("ORC-XXX") markers to E2E tests in tests/e2e/test_orchestrator_e2e.py

### Module Documentation

- [X] T097 [P] Create src/orchestrator/README.md with module documentation
- [X] T098 [P] Update CLAUDE.md with orchestrator module information

### Quality & Validation

- [X] T099 Run ruff check and fix any linting issues in src/orchestrator/
- [X] T100 Run mypy and fix any type errors in src/orchestrator/
- [X] T101 Run all tests and ensure 100% pass rate
- [X] T102 Run quickstart.md scenarios as validation
- [X] T103 Verify state machine performance meets SC-001 (< 5 min full workflow)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (State Machine): Can proceed immediately after Foundational
  - US2 (Phase 1 Execution): Depends on US1 completion
  - US3 (Agent Dispatch): Can proceed after Foundational (parallel with US1/US2)
  - US4 (Phase 2 Execution): Depends on US1, US2, US3 completion
  - US5 (Label Sync): Can proceed after Foundational (parallel with US1-US4)
- **Integration (Phase 8)**: Depends on all user stories (US1-US5) completion
- **Polish (Phase 9)**: Depends on Integration phase completion

### User Story Dependencies

```
US1 (State Machine) ─────┐
                         │
US3 (Agent Dispatch) ────┼───▶ US4 (Phase 2) ───▶ Integration
                         │
US2 (Phase 1) ───────────┘

US5 (Label Sync) ────────────────────────────────▶ Integration
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before integration
- Story complete before moving to dependent stories

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
# Can run in parallel:
T006, T007, T008, T009  # All enums
T012, T013, T014, T015, T016, T017  # All independent models
```

**Phase 3 (US1 State Machine)**:
```bash
# Tests in parallel:
T020, T021, T022, T023
```

**Phase 5 (US3 Agent Dispatch)**:
```bash
# Tests in parallel:
T043, T044, T045, T046
```

**Phase 9 (Polish)**:
```bash
# Journeys in parallel:
T090, T091, T092, T093, T094
```

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for WorkflowState transitions in tests/unit/test_state_machine.py"
Task: "Unit test for state persistence in tests/unit/test_state_machine.py"
Task: "Unit test for invalid transition handling in tests/unit/test_state_machine.py"
Task: "Unit test for state history tracking in tests/unit/test_state_machine.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (State Machine)
4. **STOP and VALIDATE**: Test state machine independently
5. State machine can track workflows without Phase 1/2 execution

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP state tracking
3. Add User Story 2 → Test independently → Automated Phase 1
4. Add User Story 3 → Test independently → Agent dispatch capability
5. Add User Story 4 → Test independently → Complete Phase 2 automation
6. Add User Story 5 → Test independently → GitHub visibility
7. Integration → Full orchestrator facade
8. Polish → Documentation and validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (State Machine)
   - Developer B: User Story 3 (Agent Dispatch) + User Story 5 (Labels)
3. Once US1+US3 complete:
   - Developer A: User Story 2 (Phase 1)
   - Developer B: User Story 4 (Phase 2)
4. Integration and Polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All methods require Google-style docstrings per Constitution
