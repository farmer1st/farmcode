"""Integration tests for MVP workflow (Phase 1, 2, Gate 1)."""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from farmcode.adapters.base import Comment, IssueContext
from farmcode.models.phase import WorkflowPhase


@pytest.mark.asyncio
async def test_mvp_workflow_end_to_end(orchestrator, mock_github_adapter, state_store):
    """Test complete MVP workflow: Create -> Phase 2 -> Gate 1 -> Approval."""

    # === Step 1: Create Feature (Phase 1) ===
    state = orchestrator.create_feature(
        title="Add User Authentication",
        description="Implement JWT-based authentication",
    )

    # Verify Phase 1 executed
    assert state.issue_number == 123
    assert state.current_phase == WorkflowPhase.PHASE_2_SPECS
    assert state.branch_name == "123-add-user-authentication"
    assert state.worktree_path.exists()

    # Verify GitHub issue created
    mock_github_adapter.create_issue.assert_called_once()

    # Verify state persisted
    loaded = state_store.load(123)
    assert loaded is not None
    assert loaded.current_phase == WorkflowPhase.PHASE_2_SPECS

    # === Step 2: Verify Phase 2 started ===
    # Check that comment was posted
    assert mock_github_adapter.post_comment.call_count >= 2  # Setup + Phase 2

    # === Step 3: Simulate @duc completion ===
    now = datetime.now()
    completion_comment = Comment(
        id="1",
        author="viollet-le-duc[bot]",
        body="✅ **Task Complete** (@duc)\n\nSpecs written to .plans/123/specs/",
        created_at=now,
    )

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Add User Authentication",
        body="Implement JWT-based authentication",
        labels=["farmcode"],
        comments=[completion_comment],
    )

    # Poll for updates
    updates = await orchestrator.poll_for_updates()

    # Verify completion detected
    agent_complete_updates = [u for u in updates if u["type"] == "agent_complete"]
    assert len(agent_complete_updates) == 1
    assert agent_complete_updates[0]["agent_handle"] == "duc"

    # Verify advanced to Gate 1
    phase_advanced_updates = [u for u in updates if u["type"] == "phase_advanced"]
    assert len(phase_advanced_updates) == 1
    assert phase_advanced_updates[0]["phase"] == WorkflowPhase.GATE_1_SPECS.value

    # Reload state
    state = state_store.load(123)
    assert state.current_phase == WorkflowPhase.GATE_1_SPECS

    # === Step 4: Simulate human approval ===
    approval_comment = Comment(
        id="2",
        author="human-reviewer",
        body="Looks good! approved",
        created_at=datetime.now(),
    )

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Add User Authentication",
        body="Implement JWT-based authentication",
        labels=["farmcode"],
        comments=[completion_comment, approval_comment],
    )

    # Poll for approval
    updates = await orchestrator.poll_for_updates()

    # Verify approval detected
    approval_updates = [u for u in updates if u["type"] == "human_approval"]
    assert len(approval_updates) == 1
    assert approval_updates[0]["approver"] == "human-reviewer"

    # Verify Gate 1 was approved and system advanced to Phase 3
    state = state_store.load(123)
    # After approval at Gate 1, system advances to Phase 3
    assert state.current_phase == WorkflowPhase.PHASE_3_PLANS
    # Check that Gate 1 in history shows approval
    gate_1_state = [ps for ps in state.phase_history if ps.phase == WorkflowPhase.GATE_1_SPECS][0]
    assert gate_1_state.human_approved is True


def test_create_feature_executes_phase_1(orchestrator, mock_github_adapter, state_store):
    """Test that creating a feature executes Phase 1."""
    state = orchestrator.create_feature("Test Feature", "Test description")

    # Verify issue created
    mock_github_adapter.create_issue.assert_called_once()

    # Verify worktree created
    assert state.worktree_path.exists()
    assert (state.worktree_path / ".plans" / "123").exists()

    # Verify auto-advanced to Phase 2
    assert state.current_phase == WorkflowPhase.PHASE_2_SPECS

    # Verify state saved
    loaded = state_store.load(state.issue_number)
    assert loaded is not None


@patch("farmcode.orchestrator.agent_dispatcher.subprocess.Popen")
def test_agent_dispatcher_spawns_claude_cli(mock_popen, mock_config):
    """Test that agent dispatcher spawns Claude CLI with correct config."""
    from farmcode.orchestrator.agent_dispatcher import AgentDispatcher
    from pathlib import Path

    # Create a real agent dispatcher (not mocked)
    dispatcher = AgentDispatcher()

    # Mock subprocess
    mock_popen.return_value = MagicMock(pid=12345)

    # Dispatch agent
    process = dispatcher.dispatch(
        agent_handle="duc",
        issue_number=123,
        worktree_path=Path("/tmp/test-worktree"),
        phase=WorkflowPhase.PHASE_2_SPECS,
    )

    # Verify process spawned
    mock_popen.assert_called_once()
    call_args = mock_popen.call_args

    # Verify command includes claude CLI
    cmd = call_args[0][0]
    assert cmd[0] == "claude"
    assert "--model" in cmd

    # Verify environment variables
    env = call_args[1]["env"]
    assert env["FARMCODE_AGENT_HANDLE"] == "duc"
    assert env["FARMCODE_ISSUE_NUMBER"] == "123"
    assert "FARMCODE_MCP_SERVER_URL" in env

    # Verify working directory
    assert call_args[1]["cwd"] == "/tmp/test-worktree"


def test_manual_gate_approval(orchestrator, state_store, mock_github_adapter):
    """Test manually approving a gate via orchestrator."""
    # Create feature and advance to gate
    state = orchestrator.create_feature("Test", "Test")

    # Manually complete duc
    state.mark_agent_complete("duc")
    state.advance()
    state_store.save(state)

    assert state.current_phase == WorkflowPhase.GATE_1_SPECS

    # Approve gate
    result = orchestrator.approve_gate(state.issue_number)

    # Verify approval worked and system advanced to Phase 3
    assert result is True
    loaded = state_store.load(state.issue_number)
    # After approval, system advances to Phase 3
    assert loaded.current_phase == WorkflowPhase.PHASE_3_PLANS
    # Check that Gate 1 in history shows approval
    gate_1_state = [ps for ps in loaded.phase_history if ps.phase == WorkflowPhase.GATE_1_SPECS][0]
    assert gate_1_state.human_approved is True


def test_list_all_features(orchestrator, state_store):
    """Test listing all active features."""
    # Create multiple features
    state1 = orchestrator.create_feature("Feature 1", "Description 1")
    state2 = orchestrator.create_feature("Feature 2", "Description 2")

    # List all
    features = orchestrator.list_all_features()

    assert len(features) == 2
    issue_numbers = {f.issue_number for f in features}
    assert state1.issue_number in issue_numbers
    assert state2.issue_number in issue_numbers


def test_get_feature_state(orchestrator, state_store):
    """Test getting specific feature state."""
    # Create feature
    state = orchestrator.create_feature("Test", "Test")

    # Get state
    loaded = orchestrator.get_feature_state(state.issue_number)

    assert loaded is not None
    assert loaded.issue_number == state.issue_number
    assert loaded.title == "Test"


def test_get_nonexistent_feature(orchestrator):
    """Test getting nonexistent feature returns None."""
    loaded = orchestrator.get_feature_state(999)
    assert loaded is None


@pytest.mark.asyncio
async def test_polling_loop_with_no_updates(orchestrator, mock_github_adapter):
    """Test that polling loop handles no updates gracefully."""
    # Create feature
    orchestrator.create_feature("Test", "Test")

    # Mock no new comments
    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=[],
    )

    # Poll
    updates = await orchestrator.poll_for_updates()

    # Should have no updates
    assert len(updates) == 0


@pytest.mark.asyncio
async def test_polling_loop_with_multiple_features(orchestrator, mock_github_adapter, state_store):
    """Test polling handles multiple features."""
    # Create two features
    state1 = orchestrator.create_feature("Feature 1", "Desc 1")
    state2 = orchestrator.create_feature("Feature 2", "Desc 2")

    # Mock completions for both
    def mock_get_context(issue_id):
        return IssueContext(
            issue_number=int(issue_id),
            title=f"Feature {issue_id}",
            body="Test",
            labels=[],
            comments=[
                Comment(
                    id="1",
                    author="viollet-le-duc[bot]",
                    body="✅ Complete",
                    created_at=datetime.now(),
                )
            ],
        )

    mock_github_adapter.get_issue_context.side_effect = mock_get_context

    # Poll
    updates = await orchestrator.poll_for_updates()

    # Should have completions for both features
    completions = [u for u in updates if u["type"] == "agent_complete"]
    assert len(completions) == 2
