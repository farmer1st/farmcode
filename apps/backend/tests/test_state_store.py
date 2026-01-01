"""Tests for state store persistence."""

import pytest

from farmcode.models.phase import WorkflowPhase
from farmcode.models.state import FeatureState
from farmcode.storage.state_store import StateStore


@pytest.fixture
def feature_state(tmp_path):
    """Create a test feature state."""
    return FeatureState(
        issue_number=123,
        title="Test Feature",
        description="Test description",
        branch_name="123-test-feature",
        worktree_path=tmp_path / "123-test-feature",
        current_phase=WorkflowPhase.PHASE_2_SPECS,
        phase_history=[],
    )


def test_save_and_load_state(state_store, feature_state):
    """Test saving and loading state."""
    # Save
    state_store.save(feature_state)

    # Load
    loaded = state_store.load(123)

    assert loaded is not None
    assert loaded.issue_number == 123
    assert loaded.title == "Test Feature"
    assert loaded.current_phase == WorkflowPhase.PHASE_2_SPECS


def test_load_nonexistent_state(state_store):
    """Test loading nonexistent state returns None."""
    loaded = state_store.load(999)
    assert loaded is None


def test_delete_state(state_store, feature_state):
    """Test deleting state."""
    # Save
    state_store.save(feature_state)

    # Delete
    assert state_store.delete(123) is True

    # Verify deleted
    assert state_store.load(123) is None


def test_delete_nonexistent_state(state_store):
    """Test deleting nonexistent state returns False."""
    assert state_store.delete(999) is False


def test_list_all_states(state_store, tmp_path):
    """Test listing all states."""
    # Create multiple states
    states = [
        FeatureState(
            issue_number=i,
            title=f"Feature {i}",
            description=f"Description {i}",
            branch_name=f"{i}-feature",
            worktree_path=tmp_path / f"{i}-feature",
            current_phase=WorkflowPhase.PHASE_2_SPECS,
            phase_history=[],
        )
        for i in range(1, 4)
    ]

    # Save all
    for state in states:
        state_store.save(state)

    # List all
    loaded = state_store.list_all()

    assert len(loaded) == 3
    assert [s.issue_number for s in loaded] == [1, 2, 3]


def test_exists(state_store, feature_state):
    """Test checking if state exists."""
    assert not state_store.exists(123)

    state_store.save(feature_state)

    assert state_store.exists(123)


def test_state_persistence_preserves_phase_history(state_store, feature_state):
    """Test that phase history is preserved across save/load."""
    # Start phases
    feature_state.start_phase(WorkflowPhase.PHASE_2_SPECS)
    feature_state.mark_agent_complete("duc")

    # Save
    state_store.save(feature_state)

    # Load
    loaded = state_store.load(123)

    assert loaded is not None
    assert len(loaded.phase_history) == 1
    assert loaded.phase_history[0].phase == WorkflowPhase.PHASE_2_SPECS
    # Check that duc is in active_agents and marked as completed
    assert "duc" in loaded.phase_history[0].active_agents
    assert loaded.phase_history[0].active_agents["duc"].completed is True
