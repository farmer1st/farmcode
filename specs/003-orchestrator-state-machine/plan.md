# Implementation Plan: Orchestrator State Machine

**Branch**: `003-orchestrator-state-machine` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-orchestrator-state-machine/spec.md`

## Summary

Build a state machine that orchestrates SDLC Phases 1-2 with flexible agent dispatching. The orchestrator manages workflow state (IDLE → PHASE_1 → PHASE_2 → GATE_1 → DONE), executes Phase 1 (issue/branch/worktree setup), dispatches AI agents with a pluggable runner architecture, and synchronizes GitHub labels with workflow state.

## Technical Context

**Language/Version**: Python 3.11+ (consistent with existing modules)
**Primary Dependencies**: Pydantic v2 (models), python-dotenv (config), subprocess (CLI runner)
**Storage**: JSON file in .plans directory (state persistence)
**Testing**: pytest with pytest-asyncio, contract/integration/e2e tests
**Target Platform**: Local CLI (macOS/Linux)
**Project Type**: Single Python library module (src/orchestrator/)
**Performance Goals**: Phase 1 < 30s, agent dispatch < 5s, label sync < 2s
**Constraints**: Must work offline for state machine, online for GitHub operations
**Scale/Scope**: Single-user developer tool

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Test-First Development | COMPLIANT | Contract tests before implementation |
| II. Specification-Driven | COMPLIANT | Spec complete, plan in progress |
| III. Independent User Stories | COMPLIANT | 5 prioritized stories (P1-P5) |
| IV. Human Approval Gates | COMPLIANT | Gate 1 pending (this plan) |
| V. Parallel-First Execution | COMPLIANT | Stories P3-P5 can parallel after P1-P2 |
| VI. Simplicity and YAGNI | COMPLIANT | Only ClaudeCLIRunner implemented, others future |
| VII. Versioning | COMPLIANT | Conventional commits enforced |
| VIII. Technology Stack | COMPLIANT | Python 3.11+, Pydantic v2, pytest |
| IX. Thin Client | N/A | No frontend in this feature |
| X. Security-First | COMPLIANT | No secrets in code, env vars for config |
| XI. Documentation | COMPLIANT | User journeys mapped, docstrings required |
| XII. CI/CD | COMPLIANT | Tests in CI, E2E with real APIs |

**Result**: All gates PASS. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/003-orchestrator-state-machine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── orchestrator-service.md
│   └── agent-runner.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── github_integration/  # Feature 001 - existing
├── worktree_manager/    # Feature 002 - existing
└── orchestrator/        # Feature 003 - NEW
    ├── __init__.py      # Public exports
    ├── models.py        # State, AgentConfig, Phase models
    ├── errors.py        # Custom exceptions
    ├── state_machine.py # Core state machine logic
    ├── phase_executor.py # Phase 1 & 2 execution
    ├── agent_runner.py  # AgentRunner protocol + ClaudeCLIRunner
    ├── label_sync.py    # GitHub label synchronization
    ├── polling.py       # Comment signal polling
    └── service.py       # OrchestratorService facade

tests/
├── contract/
│   └── test_orchestrator_contract.py
├── integration/
│   └── test_orchestrator_integration.py
├── e2e/
│   └── test_orchestrator_e2e.py
└── unit/
    ├── test_state_machine.py
    ├── test_agent_runner.py
    ├── test_phase_executor.py
    └── test_polling.py
```

**Structure Decision**: Single project layout matching existing modules (github_integration, worktree_manager). New orchestrator module follows same patterns.

## User Journey Mapping (REQUIRED per Constitution Principle XI)

**Journey Domain**: ORC (Orchestrator)

| User Story | Journey ID | Journey Name | Priority |
|------------|------------|--------------|----------|
| US1: State Machine Core | ORC-001 | Track workflow state | P1 |
| US2: Phase 1 Execution | ORC-002 | Setup feature infrastructure | P2 |
| US3: Agent Dispatch | ORC-003 | Dispatch AI agent | P3 |
| US4: Phase 2 Execution | ORC-004 | Execute specification phase | P4 |
| US5: Label Sync | ORC-005 | Sync labels with state | P5 |

**Journey Files to Create**:
- `docs/user-journeys/ORC-001-track-workflow-state.md`
- `docs/user-journeys/ORC-002-setup-feature-infrastructure.md`
- `docs/user-journeys/ORC-003-dispatch-ai-agent.md`
- `docs/user-journeys/ORC-004-execute-specification-phase.md`
- `docs/user-journeys/ORC-005-sync-labels-with-state.md`
- Update `docs/user-journeys/JOURNEYS.md`

**E2E Test Markers**:
- Each E2E test class should be marked with `@pytest.mark.journey("ORC-NNN")`

## Complexity Tracking

> No complexity tracking needed - all principles compliant.
