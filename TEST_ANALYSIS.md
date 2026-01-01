# Test Failure Analysis Report

## Executive Summary

**Verdict: The IMPLEMENTATION is correct. The TESTS are outdated.**

The tests were written for a simpler, earlier design that was refined during implementation. The current implementation follows better software engineering practices and aligns with the specifications.

---

## Specification Review

### From `references/sdlc-workflow.md`

The SDLC workflow spec defines:

1. **8-Phase Workflow** with 4 human approval gates
2. **Agent Completion Detection** via polling for `✅` comments in GitHub issues
3. **State Tracking** for:
   - Which phase the feature is in
   - Which agents are active in current phase
   - Which agents have completed
   - Whether human has approved gates

### From `docs/mcp-tools-spec.md`

The MCP tools spec defines how agents signal completion:

```bash
✅ Backend plan complete. See `.plans/123/backend.md`.

@baron Ready for next phase.
```

**Key Point:** The spec doesn't prescribe exact data structures, but describes the workflow behavior.

---

## Implementation Analysis

### Current Implementation (✅ CORRECT)

**`PhaseState` Model** (`farmcode/models/state.py:24-32`):
```python
class AgentCompletion(BaseModel):
    agent_handle: str
    completed: bool = False
    completed_at: datetime | None = None
    artifact_path: str | None = None
    comment_id: str | None = None

class PhaseState(BaseModel):
    phase: WorkflowPhase
    started_at: datetime | None = None
    completed_at: datetime | None = None
    active_agents: dict[str, AgentCompletion]  # Dict mapping agent -> completion
    human_approved: bool                        # Explicit naming
    human_approved_at: datetime | None
```

**`FeatureState` Helper Methods** (`farmcode/models/state.py:103-130`):
```python
def all_agents_complete(self) -> bool:
    """Check if all agents in the current phase are complete."""
    phase_state = self.get_current_phase_state()
    if not phase_state or not phase_state.active_agents:
        return True
    return all(agent.completed for agent in phase_state.active_agents.values())

def can_advance(self) -> bool:
    """Check if the workflow can advance to the next phase."""
    if self.current_phase.is_terminal():
        return False
    if self.current_phase.is_gate():
        phase_state = self.get_current_phase_state()
        return phase_state.human_approved if phase_state else False
    return self.all_agents_complete()
```

**Why This is Better:**
1. ✅ **Rich metadata** - Tracks when, what artifacts, which comment ID
2. ✅ **Type safety** - Dict of structured objects vs list of strings
3. ✅ **Explicit naming** - `human_approved` is clearer than `approved`
4. ✅ **Proper encapsulation** - `all_agents_complete()` is a method, not exposed state
5. ✅ **Aligns with specs** - Supports the workflow described in SDLC doc

---

## Test Expectations (❌ OUTDATED)

### What Tests Expect

**Tests assume PhaseState has:**
```python
class PhaseState:  # What tests expect (WRONG)
    agents_complete: list[str]      # Simple list
    approved: bool                   # Generic name
    all_agents_complete: ???         # Unclear if property or field
```

**Evidence from test failures:**
```
AttributeError: 'PhaseState' object has no attribute 'agents_complete'
AttributeError: 'PhaseState' object has no attribute 'approved'
AttributeError: 'PhaseState' object has no attribute 'all_agents_complete'
ValueError: "PhaseState" object has no field "approved"
```

### Why Tests Are Wrong

1. **Simpler design** - Tests expect a list of strings instead of rich completion objects
2. **Less specific naming** - `approved` instead of `human_approved`
3. **Wrong API** - Expects `all_agents_complete` on `PhaseState` instead of `FeatureState`
4. **Missing fields** - Tests expect fields that were never implemented

---

## Issue-by-Issue Breakdown

### Issue #1: Comment Model Missing `id` (5 failures)

**Tests:** `test_github_poller.py`

**Problem:**
```python
# Tests create Comment without required 'id' field
Comment(
    author="viollet-le-duc",
    created_at=now,
    body="✅ Specs complete..."
)
# Error: ValidationError: id - Field required
```

**Root Cause:** Tests don't provide the `id` field that `Comment` model requires.

**From Spec:** `docs/mcp-tools-spec.md:305-316` shows comments have IDs:
```json
{
  "comments": [
    {
      "id": 456792,  // ← ID is part of spec
      "author": "duc",
      "created_at": "2025-01-01T10:15:00Z",
      "body": "..."
    }
  ]
}
```

**Verdict:** **Implementation is correct, tests need fixing.**

---

### Issue #2: PhaseState API Mismatch (8 failures)

**Tests:** `test_state_machine.py`, `test_state_store.py`

**Problem:** Tests try to access:
- `phase_state.agents_complete` ❌ (doesn't exist)
- `phase_state.approved` ❌ (should be `human_approved`)
- `phase_state.all_agents_complete` ❌ (method is on `FeatureState`)

**From Spec:** SDLC workflow doesn't prescribe exact field names, but describes behavior:
- Track which agents completed ✅ (via `active_agents` dict)
- Track human approval ✅ (via `human_approved` field)
- Check if all agents done ✅ (via `FeatureState.all_agents_complete()` method)

**Verdict:** **Implementation is correct and better designed, tests need updating.**

---

### Issue #3: Missing `get_settings()` Function (10 errors)

**Tests:** `test_mvp_integration.py`, `test_github_poller.py`

**Problem:**
```python
# tests/conftest.py:69
monkeypatch.setattr(
    "farmcode.adapters.github_adapter.get_settings",
    mock_get_settings
)
# Error: AttributeError: module has no attribute 'get_settings'
```

**Root Cause:** Test fixture tries to mock a function that was never implemented.

**Verdict:** **Test fixture is wrong, needs fixing.**

---

### Issue #4: Git Mock Setup (10 errors)

**Tests:** `test_phase_manager.py`, `test_worktree_manager.py`

**Problem:**
```python
# tests/conftest.py:149
repo.head.reference = repo.heads.main = repo.create_head("main")
# Error: AttributeError: 'IterableList' object has no attribute 'main'
```

**Root Cause:** Incorrect git mock setup. GitPython's API doesn't work this way.

**Verdict:** **Test fixture is broken, needs fixing.**

---

## Recommendation

### Fix Strategy: Update Tests to Match Implementation

**Priority 1: Fix PhaseState API Usage**
- Replace `phase_state.agents_complete` with proper access to `active_agents` dict
- Replace `phase_state.approved` with `phase_state.human_approved`
- Move `all_agents_complete()` calls to `FeatureState` level

**Priority 2: Fix Comment Model Usage**
- Add `id` field to all `Comment` objects in tests

**Priority 3: Fix Test Fixtures**
- Remove or fix `get_settings()` mock
- Fix git repository mock setup

**Priority 4: Update Test Assertions**
- Update all assertions to match actual implementation API

---

## Why Implementation is Superior

### The Old Design (What Tests Expect)
```python
phase_state.agents_complete = ["duc"]  # Just a list of strings
phase_state.approved = True            # When? Who? What comment?
```

**Problems:**
- ❌ No timestamp of when agent completed
- ❌ No reference to which artifact was created
- ❌ No link back to GitHub comment
- ❌ Can't distinguish between "not started" and "incomplete"

### The New Design (Current Implementation)
```python
phase_state.active_agents = {
    "duc": AgentCompletion(
        agent_handle="duc",
        completed=True,
        completed_at=datetime(2025, 1, 1, 10, 30),
        artifact_path=".plans/123/specs/backend.md",
        comment_id="456789"
    )
}
phase_state.human_approved = True
phase_state.human_approved_at = datetime(2025, 1, 1, 11, 0)
```

**Benefits:**
- ✅ Full audit trail
- ✅ Links back to GitHub comments
- ✅ Tracks artifacts produced
- ✅ Timestamped approvals
- ✅ Distinguishes "pending" from "not assigned"

---

## Conclusion

The **implementation follows best practices** and provides the functionality described in the specifications with **better data modeling** than the tests expected.

The **tests were written for an earlier, simpler design** and need to be updated to match the superior implementation.

**Next Steps:**
1. Update all tests to use the correct PhaseState API
2. Fix Comment object creation to include `id` field
3. Fix or remove broken test fixtures
4. Run tests again to verify

**Status:** Implementation ✅ | Tests ❌ | Specs ✅
