# User Journeys

Complete list of all user journeys for FarmCode orchestrator.

## Journey Domains

| Domain | Description |
|--------|-------------|
| **ORC** | Orchestrator - AI agent workflow orchestration and SDLC management |
| **GH**  | GitHub - Direct GitHub integration operations (future) |
| **UI**  | User Interface - Web/TUI user interactions (future) |

## All Journeys

| Journey ID | Name | Priority | Status | Test Coverage | E2E Tests |
|------------|------|----------|--------|---------------|-----------|
| [ORC-001](./ORC-001-create-issue.md) | Create Issue for New Feature Request | P1 | ✅ Implemented | ✅ 100% | 1/1 passing |
| [ORC-002](./ORC-002-agent-feedback.md) | Agent Provides Feedback via Comment | P2 | 📋 Planned | ⏳ 0% | 0/0 tests |
| [ORC-003](./ORC-003-workflow-progression.md) | Progress Issue Through Workflow Phases | P2 | 📋 Planned | ⏳ 0% | 0/0 tests |
| [ORC-004](./ORC-004-link-pull-request.md) | Link Pull Request to Feature Issue | P3 | 📋 Planned | ⏳ 0% | 0/0 tests |
| [ORC-005](./ORC-005-full-sdlc-workflow.md) | Complete 8-Phase SDLC Workflow | P1 | ✅ Implemented | ✅ 100% | 1/1 passing |

## Status Legend

- ✅ **Implemented**: Fully implemented with passing tests
- 🚧 **In Progress**: Currently being developed
- 📋 **Planned**: Designed but not yet implemented
- ⏸️ **Paused**: Development temporarily halted
- ❌ **Deprecated**: No longer supported

## Coverage by Priority

### P1 Journeys (Critical - Required for MVP)
| ID | Name | Status | Coverage |
|----|------|--------|----------|
| ORC-001 | Create Issue for New Feature Request | ✅ Implemented | 100% |
| ORC-005 | Complete 8-Phase SDLC Workflow | ✅ Implemented | 100% (partial) |

**P1 Coverage**: 2/2 implemented (100%)

### P2 Journeys (Important - Post-MVP)
| ID | Name | Status | Coverage |
|----|------|--------|----------|
| ORC-002 | Agent Provides Feedback via Comment | 📋 Planned | 0% |
| ORC-003 | Progress Issue Through Workflow Phases | 📋 Planned | 0% |

**P2 Coverage**: 0/2 implemented (0%)

### P3 Journeys (Nice to Have)
| ID | Name | Status | Coverage |
|----|------|--------|----------|
| ORC-004 | Link Pull Request to Feature Issue | 📋 Planned | 0% |

**P3 Coverage**: 0/1 implemented (0%)

## Test Coverage Visualization

```
Overall Journey Coverage:
ORC-001: ████████████████████ 100% (1/1 E2E tests passing)
ORC-002: ░░░░░░░░░░░░░░░░░░░░   0% (not yet implemented)
ORC-003: ░░░░░░░░░░░░░░░░░░░░   0% (not yet implemented)
ORC-004: ░░░░░░░░░░░░░░░░░░░░   0% (not yet implemented)
ORC-005: ████████████████████ 100% (1/1 E2E tests passing)

Total: 2/5 journeys implemented (40%)
P1 Journeys: 2/2 implemented (100%) ✅
```

## Journeys by Feature

### Feature 001: GitHub Integration Core

| User Story | Journeys | Status |
|------------|----------|--------|
| US1: Create and Track Issues | ORC-001 | ✅ Implemented |
| US2: Capture Agent Feedback | ORC-002 | 📋 Planned |
| US3: Manage Workflow State | ORC-003 | 📋 Planned |
| US4: Link PRs to Issues | ORC-004 | 📋 Planned |
| All Stories Combined | ORC-005 | ✅ Partial |

### Future Features

| Feature | Journeys | Status |
|---------|----------|--------|
| Feature 002: TUI Interface | UI-001 to UI-010 | 🔮 Not yet planned |
| Feature 003: Orchestrator Logic | ORC-006 to ORC-015 | 🔮 Not yet planned |
| Feature 004: Advanced GitHub | GH-001 to GH-005 | 🔮 Not yet planned |

## Running Journey Tests

```bash
# Run all journey-tagged tests
pytest -m journey -v

# Run specific journey
pytest -m "journey('ORC-001')" -v

# Generate journey coverage report (automatically shown at end of test run)
pytest -m journey

# See which tests are tagged with journeys
pytest --co -m journey
```

## Journey Coverage Goals

**Release Criteria:**
- **v1.0 (MVP)**: All P1 journeys 100% tested ✅ **ACHIEVED**
- **v1.1**: 80%+ of P2 journeys tested
- **v1.2**: All P2 journeys 100% tested
- **v2.0**: All P3 journeys tested

**Current Status**: v1.0 MVP ready (P1 journeys complete)

## Related Documentation

- [Journey Documentation Guide](./README.md) - How to write and maintain journey docs
- [Constitution - Principle XI](../../.specify/memory/constitution.md#xi-documentation-and-user-journeys) - Journey standards
- [E2E Test Guide](../testing/e2e-tests.md) - How to write journey tests (future)
- [SDLC Workflow Reference](../../references/sdlc-workflow.md) - The 8-phase workflow

## Last Updated

**Date**: 2026-01-02
**By**: GitHub Integration Core implementation
**Next Review**: After implementing User Story 2 (Comments)
