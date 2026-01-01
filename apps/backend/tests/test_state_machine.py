"""Tests for state machine phase transitions."""

import pytest

from farmcode.models.phase import WorkflowPhase
from farmcode.models.state import FeatureState
from farmcode.orchestrator.state_machine import StateMachine


@pytest.fixture
def feature_state(tmp_path):
    """Create a test feature state."""
    state = FeatureState(
        issue_number=123,
        title="Test Feature",
        description="Test description",
        branch_name="123-test-feature",
        worktree_path=tmp_path / "123-test-feature",
        current_phase=WorkflowPhase.PHASE_2_SPECS,
        phase_history=[],
    )
    state.start_phase(WorkflowPhase.PHASE_2_SPECS)
    return state


def test_state_machine_initialization(feature_state):
    """Test state machine can be initialized."""
    machine = StateMachine(feature_state)
    assert machine.state == feature_state


def test_cannot_advance_without_agents_complete(feature_state):
    """Test that work phase cannot advance until agents complete."""
    machine = StateMachine(feature_state)

    # Phase 2 requires duc to complete
    assert not machine.can_advance()


def test_can_advance_after_agent_complete(feature_state):
    """Test that phase can advance after all agents complete."""
    machine = StateMachine(feature_state)

    # Mark duc complete
    assert machine.handle_agent_complete("duc")

    # Should now be able to advance
    assert machine.can_advance()


def test_advance_to_next_phase(feature_state):
    """Test advancing to next phase."""
    machine = StateMachine(feature_state)

    # Mark agent complete
    machine.handle_agent_complete("duc")

    # Advance
    assert machine.advance()
    assert feature_state.current_phase == WorkflowPhase.GATE_1_SPECS


def test_cannot_advance_without_approval_at_gate(feature_state):
    """Test that gate phase requires approval."""
    # Advance to gate
    feature_state.mark_agent_complete("duc")
    feature_state.advance()

    machine = StateMachine(feature_state)
    assert feature_state.current_phase == WorkflowPhase.GATE_1_SPECS
    assert not machine.can_advance()


def test_can_advance_after_approval(feature_state):
    """Test that gate can advance after approval."""
    # Advance to gate
    feature_state.mark_agent_complete("duc")
    feature_state.advance()

    machine = StateMachine(feature_state)

    # Approve
    machine.handle_human_approval()

    # Should now be able to advance
    assert machine.can_advance()


def test_handle_agent_complete_for_wrong_phase(feature_state):
    """Test that agent completion for wrong phase is rejected."""
    machine = StateMachine(feature_state)

    # Try to mark baron complete (not in Phase 2)
    assert not machine.handle_agent_complete("baron")


def test_get_status_summary(feature_state):
    """Test getting status summary."""
    machine = StateMachine(feature_state)

    status = machine.get_status_summary()

    assert status["phase"] == WorkflowPhase.PHASE_2_SPECS.value
    assert status["is_gate"] is False
    assert status["can_advance"] is False
    assert len(status["agents"]) == 1
    assert status["agents"][0]["handle"] == "duc"
    assert status["agents"][0]["complete"] is False


def test_get_status_summary_at_gate(feature_state):
    """Test getting status summary at gate."""
    # Advance to gate
    feature_state.mark_agent_complete("duc")
    feature_state.advance()

    machine = StateMachine(feature_state)
    status = machine.get_status_summary()

    assert status["phase"] == WorkflowPhase.GATE_1_SPECS.value
    assert status["is_gate"] is True
    assert status["approved"] is False
