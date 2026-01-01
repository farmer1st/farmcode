"""Tests for phase manager."""

import pytest

from farmcode.models.phase import WorkflowPhase
from farmcode.orchestrator.phase_manager import PhaseManager


@pytest.fixture
def phase_manager(mock_worktree_manager, mock_github_adapter):
    """Create a phase manager."""
    return PhaseManager(
        worktree_manager=mock_worktree_manager,
        github_adapter=mock_github_adapter,
    )


def test_execute_phase_1(phase_manager, mock_github_adapter, mock_config):
    """Test executing Phase 1."""
    state = phase_manager.execute_phase_1(
        title="Add Dark Mode",
        description="Implement dark mode toggle",
    )

    # Verify issue created
    mock_github_adapter.create_issue.assert_called_once()
    call_args = mock_github_adapter.create_issue.call_args
    assert call_args[1]["title"] == "Add Dark Mode"
    assert "farmcode" in call_args[1]["labels"]

    # Verify state initialized
    assert state.issue_number == 123
    assert state.title == "Add Dark Mode"
    assert state.branch_name == "123-add-dark-mode"
    assert state.current_phase == WorkflowPhase.PHASE_1_SETUP

    # Verify worktree created
    assert state.worktree_path.exists()
    assert (state.worktree_path / ".plans" / "123").exists()

    # Verify Phase 1 is in phase history (auto-completes since it has no agents)
    # Phase 1 is not a gate, so it doesn't have approved/human_approved
    # It's complete when all_agents_complete returns True (which it does for empty agents)
    assert len(state.phase_history) == 1
    assert state.phase_history[0].phase == WorkflowPhase.PHASE_1_SETUP


def test_execute_phase_2(phase_manager, mock_github_adapter, tmp_path):
    """Test executing Phase 2."""
    # Create a mock state
    from farmcode.models.state import FeatureState

    state = FeatureState(
        issue_number=123,
        title="Test Feature",
        description="Test",
        branch_name="123-test",
        worktree_path=tmp_path / "123-test",
        current_phase=WorkflowPhase.PHASE_2_SPECS,
        phase_history=[],
    )

    # Execute Phase 2
    phase_manager.execute_phase_2(state)

    # Verify comment posted
    mock_github_adapter.post_comment.assert_called_once()
    call_args = mock_github_adapter.post_comment.call_args

    # Verify comment mentions @duc
    comment_body = call_args[1]["body"]
    assert "@duc" in comment_body
    assert "Phase 2" in comment_body
    assert "specs" in comment_body.lower()


def test_execute_phase_2_wrong_phase_raises_error(phase_manager, tmp_path):
    """Test that executing Phase 2 from wrong phase raises error."""
    from farmcode.models.state import FeatureState

    state = FeatureState(
        issue_number=123,
        title="Test",
        description="Test",
        branch_name="123-test",
        worktree_path=tmp_path,
        current_phase=WorkflowPhase.PHASE_1_SETUP,  # Wrong phase
        phase_history=[],
    )

    with pytest.raises(ValueError, match="Cannot execute Phase 2"):
        phase_manager.execute_phase_2(state)


def test_execute_gate_1(phase_manager, mock_github_adapter, tmp_path):
    """Test executing Gate 1."""
    from farmcode.models.state import FeatureState

    state = FeatureState(
        issue_number=123,
        title="Test",
        description="Test",
        branch_name="123-test",
        worktree_path=tmp_path,
        current_phase=WorkflowPhase.GATE_1_SPECS,
        phase_history=[],
    )

    # Execute Gate 1
    phase_manager.execute_gate_1(state)

    # Verify approval request posted
    mock_github_adapter.post_comment.assert_called_once()
    call_args = mock_github_adapter.post_comment.call_args

    comment_body = call_args[1]["body"]
    assert "Gate 1" in comment_body
    assert "approval" in comment_body.lower()
    assert ".plans/123/specs/" in comment_body


def test_execute_gate_1_wrong_phase_raises_error(phase_manager, tmp_path):
    """Test that executing Gate 1 from wrong phase raises error."""
    from farmcode.models.state import FeatureState

    state = FeatureState(
        issue_number=123,
        title="Test",
        description="Test",
        branch_name="123-test",
        worktree_path=tmp_path,
        current_phase=WorkflowPhase.PHASE_2_SPECS,  # Wrong phase
        phase_history=[],
    )

    with pytest.raises(ValueError, match="Cannot execute Gate 1"):
        phase_manager.execute_gate_1(state)
