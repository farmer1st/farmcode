# Farm Code Development Methodology

This document defines the mandatory development process for all Farm Code features.

## Development Workflow

Every feature MUST follow this exact sequence:

### 1. Specification Phase
**Owner**: Developer proposes, User approves

1. Write detailed specification document in `docs/specs/`
2. Include:
   - Feature overview and rationale
   - Architecture design
   - API/interface contracts
   - Data models
   - User flows (if UI)
   - Success criteria
3. Submit for approval
4. **GATE**: Wait for user approval before proceeding
5. Only after approval → proceed to test phase

### 2. Test Definition Phase
**Owner**: Developer writes, User reviews

Write tests in this order:

#### A. Unit Tests (`tests/unit/`)
- Test individual functions/classes in isolation
- Mock all external dependencies
- Fast execution (< 1ms per test)
- **Goal**: Verify component logic correctness

**Naming**: `test_<component>_<function>.py`

Example:
```python
# tests/unit/test_state_machine_advance.py
def test_can_advance_after_all_agents_complete():
    """Test phase advancement when all agents done."""
    # ... test code
```

#### B. Integration Tests (`tests/integration/`)
- Test multiple components working together
- Mock only external APIs (GitHub, Claude)
- Moderate execution time (< 100ms per test)
- **Goal**: Verify component interactions

**Naming**: `test_<feature>_integration.py`

Example:
```python
# tests/integration/test_phase_transition_integration.py
def test_phase_2_to_gate_1_transition():
    """Test Phase 2 completes and advances to Gate 1."""
    # Uses real StateStore, StateMachine, PhaseManager
    # Mocks GitHub API
```

#### C. End-to-End Tests (`tests/e2e/`)
- Test complete user workflows
- Mock only external services we don't control (GitHub API)
- Slower execution (< 1s per test)
- **Goal**: Verify feature works as user experiences it

**Naming**: `test_<workflow>_e2e.py`

Example:
```python
# tests/e2e/test_feature_creation_e2e.py
async def test_create_feature_through_approval():
    """Test complete workflow: Create → Specs → Approval."""
    # Full orchestrator + all real components
    # Only mocks GitHub API calls
```

#### Test Structure Requirements

Each test file MUST include:
```python
"""
Tests for <component/feature>.

Test Type: [Unit | Integration | E2E]
Coverage: <what this file tests>

Setup:
- <fixtures used>
- <mocks used>

Scenarios:
- ✅ Happy path
- ✅ Edge cases
- ✅ Error conditions
"""
```

### 3. Verification Phase
**Owner**: Developer verifies, User validates

1. Run all tests → **ALL MUST FAIL** (red phase)
2. Document failures:
   ```bash
   pytest tests/ -v > test_failures.txt
   ```
3. Verify failures are for the RIGHT reasons:
   - Not import errors
   - Not syntax errors
   - Failing because feature not implemented
4. Submit test suite for review
5. **GATE**: Wait for user validation of test coverage

### 4. Implementation Phase
**Owner**: Developer implements

1. Implement feature to make tests pass
2. Follow TDD cycle:
   - Pick ONE failing test
   - Write minimal code to pass it
   - Run test → verify pass
   - Refactor if needed
   - Commit
   - Repeat
3. **DO NOT** add untested code
4. **DO NOT** skip failing tests
5. Keep running full test suite:
   ```bash
   pytest tests/ --cov=farmcode -v
   ```
6. When all tests green → proceed to validation

### 5. Validation Phase
**Owner**: Developer validates, User accepts

1. Run full test suite with coverage:
   ```bash
   pytest tests/ --cov=farmcode --cov-report=html --cov-report=term
   ```
2. Verify:
   - ✅ All tests pass
   - ✅ Coverage ≥ 90% for new code
   - ✅ No skipped tests
   - ✅ No warnings
3. Run linting:
   ```bash
   ruff check farmcode
   mypy farmcode
   ```
4. Manual testing (if UI):
   - Test happy path
   - Test error conditions
5. Document results
6. **GATE**: Submit for user acceptance

---

## Test Categories

### Unit Tests
**Location**: `tests/unit/`

**Purpose**: Test single units of code in complete isolation.

**Characteristics**:
- Mock ALL dependencies
- Test one function/method
- Fast (< 1ms)
- No I/O operations
- Deterministic

**Example**:
```python
def test_slugify_converts_spaces_to_hyphens():
    manager = WorktreeManager.__new__(WorktreeManager)
    assert manager._slugify("Add User Auth") == "add-user-auth"
```

**When to write**:
- Testing pure functions
- Testing class methods
- Testing validation logic
- Testing calculations

---

### Integration Tests
**Location**: `tests/integration/`

**Purpose**: Test multiple components working together.

**Characteristics**:
- Use REAL internal components
- Mock ONLY external APIs
- Moderate speed (< 100ms)
- Tests component contracts
- May use temp files/DB

**Example**:
```python
def test_orchestrator_advances_phase_after_agent_complete():
    # Real: Orchestrator, StateMachine, StateStore
    # Mock: GitHubAdapter
    orchestrator = Orchestrator(github_adapter=mock_github)
    state = orchestrator.create_feature("Test", "Test")
    # ... verify phase advancement
```

**When to write**:
- Testing workflows across components
- Testing state persistence
- Testing event handling
- Testing error propagation

---

### End-to-End Tests
**Location**: `tests/e2e/`

**Purpose**: Test complete user workflows from start to finish.

**Characteristics**:
- Use ALL real internal components
- Mock ONLY external services (GitHub, Claude API)
- Slower (< 1s)
- Tests user scenarios
- May spawn processes

**Example**:
```python
async def test_mvp_workflow_create_to_approval():
    """Test: User creates feature → @duc writes specs → User approves"""
    # Real: Everything except GitHub API
    # Simulates complete user experience
```

**When to write**:
- Testing complete user workflows
- Testing multi-phase processes
- Testing system behavior
- Validating acceptance criteria

---

## Coverage Requirements

### Minimum Coverage Targets
- **Unit tests**: 95% of component logic
- **Integration tests**: 90% of component interactions
- **E2E tests**: 100% of user workflows

### What Must Be Tested
- ✅ All public APIs
- ✅ All state transitions
- ✅ All error conditions
- ✅ All user workflows
- ✅ All validation logic

### What Can Skip Tests
- ❌ Type hints (mypy covers this)
- ❌ Simple getters/setters
- ❌ `__repr__` / `__str__`
- ❌ Obvious delegations

---

## Test Organization

```
tests/
├── unit/                      # Unit tests (fast, isolated)
│   ├── test_state_machine.py
│   ├── test_worktree_manager.py
│   └── test_github_poller.py
├── integration/               # Integration tests (components together)
│   ├── test_phase_transitions.py
│   ├── test_agent_dispatch.py
│   └── test_state_persistence.py
├── e2e/                       # End-to-end tests (user workflows)
│   ├── test_mvp_workflow.py
│   ├── test_feature_creation.py
│   └── test_approval_flow.py
├── fixtures/                  # Shared test data
│   ├── mock_issues.py
│   └── mock_comments.py
└── conftest.py               # Shared fixtures and config
```

---

## Example: Full Development Cycle

### Step 1: Specification
```markdown
# Spec: Phase 3 - Implementation Plans

## Overview
After specs approved, @baron creates implementation plans.

## Architecture
- Phase 3 executes after Gate 1 approval
- Dispatches @baron agent
- @baron writes plans to `.plans/{issue}/plans/`
- Posts completion comment with ✅
- Advances to Gate 2

## Success Criteria
- [ ] Phase 3 can be triggered
- [ ] @baron is dispatched correctly
- [ ] Plans written to correct location
- [ ] Completion detected via polling
- [ ] Auto-advances to Gate 2
```

**GATE: User approves spec** ✅

### Step 2: Write Tests (All Failing)

**Unit test**:
```python
# tests/unit/test_phase_manager_phase_3.py
def test_execute_phase_3_posts_comment():
    """Test Phase 3 posts @baron comment."""
    # FAILS: execute_phase_3 not implemented
```

**Integration test**:
```python
# tests/integration/test_phase_3_integration.py
def test_phase_3_dispatches_baron():
    """Test Phase 3 dispatches @baron with correct config."""
    # FAILS: Phase 3 execution not implemented
```

**E2E test**:
```python
# tests/e2e/test_phase_3_e2e.py
async def test_complete_workflow_through_phase_3():
    """Test workflow from creation through Phase 3."""
    # FAILS: Phase 3 not implemented
```

**Verification**:
```bash
$ pytest tests/ -v
# ALL tests fail ❌
# Failures are because Phase 3 not implemented ✅
```

**GATE: User validates test coverage** ✅

### Step 3: Implement (TDD)

**Iteration 1**:
```python
# farmcode/orchestrator/phase_manager.py
def execute_phase_3(self, state: FeatureState) -> None:
    # Minimal implementation to pass first test
    self.github_adapter.post_comment(...)
```

```bash
$ pytest tests/unit/test_phase_manager_phase_3.py::test_execute_phase_3_posts_comment
# PASSES ✅
```

**Iteration 2**:
```python
# Add agent dispatch
def execute_phase_3(self, state: FeatureState) -> None:
    self.github_adapter.post_comment(...)
    # Dispatch @baron
```

```bash
$ pytest tests/integration/test_phase_3_integration.py
# PASSES ✅
```

**Continue until all tests pass...**

### Step 4: Validation

```bash
$ pytest tests/ --cov=farmcode --cov-report=term
# All tests pass ✅
# Coverage: 92% ✅

$ ruff check farmcode
# No issues ✅

$ mypy farmcode
# No errors ✅
```

**GATE: User acceptance** ✅

---

## Mandatory Checklist

Before submitting ANY feature:

- [ ] Spec written and approved
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] E2E tests written
- [ ] All tests failed initially (red phase)
- [ ] Implementation complete (green phase)
- [ ] All tests pass
- [ ] Coverage ≥ 90%
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Manual testing complete (if UI)

---

## Anti-Patterns (Forbidden)

### ❌ Code-First Development
```python
# NO: Writing implementation before tests
def new_feature():
    # I'll write tests later...
```

### ❌ Testing After Implementation
```python
# NO: Implementation exists, now writing tests to pass
def test_new_feature():
    # Just making sure it doesn't crash...
    assert new_feature() is not None
```

### ❌ Skipping Test Categories
```python
# NO: Only unit tests, no integration/e2e
pytest.mark.skip("Integration test, will write later")
```

### ❌ Mocking Everything in E2E
```python
# NO: E2E test that mocks all components
def test_e2e_workflow():
    orchestrator = Mock()  # This is a unit test, not e2e!
```

---

## Good Patterns (Encouraged)

### ✅ Spec-First
1. Write spec
2. Get approval
3. Write tests
4. Implement

### ✅ Red-Green-Refactor
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor while keeping tests green
4. Commit

### ✅ Layered Testing
```
E2E tests (few, slow, high value)
       ↑
Integration tests (some, moderate, component contracts)
       ↑
Unit tests (many, fast, logic coverage)
```

### ✅ Clear Test Intent
```python
def test_phase_advances_after_all_agents_complete():
    """Test phase can advance when all assigned agents mark complete.

    Given: Feature in Phase 2 with @duc assigned
    When: @duc marks complete
    Then: Phase can advance to Gate 1
    """
```

---

## Summary

**Mandatory Sequence**:
1. **Spec** → User approves
2. **Tests** (unit → integration → e2e) → User validates coverage
3. **Verify all fail** → Developer confirms
4. **Implement** (TDD cycle) → Tests go green
5. **Validate** → User accepts

**Test Pyramid**:
- Many unit tests (fast, isolated)
- Some integration tests (components together)
- Few e2e tests (complete workflows)

**Gates**:
- Spec approval required before tests
- Test validation required before implementation
- All tests must pass before acceptance

This ensures quality, maintainability, and alignment with requirements.
