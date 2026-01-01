"""Tests for GitHub comment poller."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from farmcode.adapters.base import Comment, IssueContext
from farmcode.orchestrator.github_poller import GitHubPoller


@pytest.fixture
def mock_github_adapter():
    """Create a mock GitHub adapter."""
    return MagicMock()


@pytest.fixture
def poller(mock_github_adapter):
    """Create a GitHub poller."""
    return GitHubPoller(github_adapter=mock_github_adapter)


def test_poll_for_completions_detects_completion(poller, mock_github_adapter):
    """Test detecting agent completion marker."""
    # Mock comments
    now = datetime.now()
    comments = [
        Comment(
            id="1",
            author="viollet-le-duc[bot]",
            body="✅ **Task Complete** (@duc)\n\nSpecs written to .plans/123/specs/",
            created_at=now,
        )
    ]

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=comments,
    )

    # Poll
    completions = poller.poll_for_completions(123)

    assert len(completions) == 1
    assert completions[0].agent_handle == "duc"
    assert completions[0].issue_number == 123
    assert "Specs written" in completions[0].summary


def test_poll_for_completions_filters_by_timestamp(poller, mock_github_adapter):
    """Test that polling filters comments by timestamp."""
    now = datetime.now()
    old_time = now - timedelta(hours=1)

    comments = [
        Comment(
            id="2",
            author="viollet-le-duc[bot]",
            body="✅ Old completion",
            created_at=old_time,
        ),
        Comment(
            id="3",
            author="viollet-le-duc[bot]",
            body="✅ New completion",
            created_at=now,
        ),
    ]

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=comments,
    )

    # Poll with last_check filtering out old comment
    completions = poller.poll_for_completions(
        123,
        last_check=now - timedelta(minutes=30),
    )

    assert len(completions) == 1
    assert "New completion" in completions[0].summary


def test_poll_for_approval_detects_approval(poller, mock_github_adapter):
    """Test detecting human approval."""
    now = datetime.now()
    comments = [
        Comment(
            id="4",
            author="user123",
            body="Looks good! approved",
            created_at=now,
        )
    ]

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=comments,
    )

    # Poll
    approval = poller.poll_for_approval(123)

    assert approval is not None
    assert approval.issue_number == 123
    assert approval.approver == "user123"


def test_poll_for_approval_detects_lgtm(poller, mock_github_adapter):
    """Test detecting LGTM approval."""
    now = datetime.now()
    comments = [
        Comment(
            id="5",
            author="reviewer",
            body="LGTM! Ship it.",
            created_at=now,
        )
    ]

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=comments,
    )

    # Poll
    approval = poller.poll_for_approval(123)

    assert approval is not None
    assert approval.approver == "reviewer"


def test_poll_for_approval_returns_none_without_approval(poller, mock_github_adapter):
    """Test that polling returns None without approval keywords."""
    now = datetime.now()
    comments = [
        Comment(
            id="6",
            author="user123",
            body="Needs more work",
            created_at=now,
        )
    ]

    mock_github_adapter.get_issue_context.return_value = IssueContext(
        issue_number=123,
        title="Test",
        body="Test",
        labels=[],
        comments=comments,
    )

    # Poll
    approval = poller.poll_for_approval(123)

    assert approval is None


def test_extract_agent_handle(poller, mock_config):
    """Test extracting agent handle from author."""
    assert poller._extract_agent_handle("viollet-le-duc[bot]") == "duc"
    assert poller._extract_agent_handle("baron-haussmann[bot]") == "baron"
    assert poller._extract_agent_handle("unknown-bot[bot]") is None


def test_extract_summary_from_completion(poller):
    """Test extracting summary from completion comment."""
    comment = """✅ **Task Complete** (@duc)

Wrote architecture specifications to .plans/123/specs/arch.md

**Artifacts:**
- `.plans/123/specs/arch.md`
- `.plans/123/specs/api.md`
"""

    summary = poller._extract_summary(comment)
    assert "architecture specifications" in summary.lower()
