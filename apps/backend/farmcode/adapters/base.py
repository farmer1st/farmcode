"""Base adapter interface for issue tracker agnostic operations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


class Comment(BaseModel):
    """A comment on an issue/ticket."""

    id: str
    author: str
    created_at: datetime
    body: str


class IssueContext(BaseModel):
    """Complete context for an issue/ticket."""

    issue_number: int
    title: str
    body: str
    labels: list[str]
    phase: str | None = None
    worktree_path: Path | None = None
    specs: list[dict[str, str]] = []  # [{"path": "...", "content": "..."}]
    plans: list[dict[str, str]] = []
    comments: list[Comment] = []


class IssueTrackerAdapter(Protocol):
    """Protocol for issue tracker adapters (GitHub, Jira, Linear).

    All adapters must implement these methods to work with the MCP server.
    """

    def get_issue_context(self, issue_id: str) -> IssueContext:
        """Get complete context for an issue (specs, plans, comments, etc.)."""
        ...

    def post_comment(self, issue_id: str, body: str) -> str:
        """Post a comment as the configured agent. Returns comment ID."""
        ...

    def add_label(self, issue_id: str, label: str) -> None:
        """Add a label to the issue."""
        ...

    def remove_label(self, issue_id: str, label: str) -> None:
        """Remove a label from the issue."""
        ...

    def get_comments(
        self,
        issue_id: str,
        since: datetime | None = None,
        from_author: str | None = None,
    ) -> list[Comment]:
        """Get comments on an issue, optionally filtered by time and author."""
        ...

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> str:
        """Create a new issue. Returns issue ID."""
        ...

    def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        body: str | None = None,
    ) -> None:
        """Update an issue's title or body."""
        ...

    def close_issue(self, issue_id: str, comment: str | None = None) -> None:
        """Close an issue with an optional comment."""
        ...
