"""GitHub comment poller for detecting agent completions and approvals."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from farmcode.adapters.github_adapter import GitHubAdapter
from farmcode.config import get_settings


class AgentCompletion(BaseModel):
    """Represents an agent completion signal."""

    agent_handle: str
    issue_number: int
    timestamp: datetime
    summary: str


class HumanApproval(BaseModel):
    """Represents a human approval signal."""

    issue_number: int
    timestamp: datetime
    approver: str


class GitHubPoller:
    """Polls GitHub comments for completion signals and approvals."""

    COMPLETION_MARKER = "✅"
    APPROVAL_KEYWORDS = ["approved", "lgtm", "approve"]

    def __init__(self, github_adapter: GitHubAdapter | None = None):
        """Initialize GitHub poller.

        Args:
            github_adapter: GitHub adapter. If None, creates default with "orchestrator" handle.
        """
        if github_adapter is None:
            settings = get_settings()
            github_adapter = GitHubAdapter(
                repo=settings.repository.main,
                agent_handle="orchestrator",
            )

        self.github_adapter = github_adapter

    def poll_for_completions(
        self,
        issue_number: int,
        last_check: datetime | None = None,
    ) -> list[AgentCompletion]:
        """Poll for agent completion signals (✅) in comments.

        Args:
            issue_number: GitHub issue number
            last_check: Only check comments after this time. If None, checks all.

        Returns:
            List of agent completions detected
        """
        # Get issue context with comments
        context = self.github_adapter.get_issue_context(str(issue_number))

        completions = []

        for comment in context.comments:
            # Skip if before last check
            if last_check and comment.created_at <= last_check:
                continue

            # Check for completion marker
            if self.COMPLETION_MARKER in comment.body:
                # Extract agent handle from comment author or @mention
                agent_handle = self._extract_agent_handle(comment.author)

                if agent_handle:
                    # Try to extract summary from comment
                    summary = self._extract_summary(comment.body)

                    completions.append(
                        AgentCompletion(
                            agent_handle=agent_handle,
                            issue_number=issue_number,
                            timestamp=comment.created_at,
                            summary=summary,
                        )
                    )

        return completions

    def poll_for_approval(
        self,
        issue_number: int,
        last_check: datetime | None = None,
    ) -> HumanApproval | None:
        """Poll for human approval comments.

        Args:
            issue_number: GitHub issue number
            last_check: Only check comments after this time. If None, checks all.

        Returns:
            HumanApproval if found, None otherwise
        """
        # Get issue context with comments
        context = self.github_adapter.get_issue_context(str(issue_number))

        for comment in reversed(context.comments):  # Most recent first
            # Skip if before last check
            if last_check and comment.created_at <= last_check:
                continue

            # Check for approval keywords
            comment_lower = comment.body.lower()
            if any(keyword in comment_lower for keyword in self.APPROVAL_KEYWORDS):
                return HumanApproval(
                    issue_number=issue_number,
                    timestamp=comment.created_at,
                    approver=comment.author,
                )

        return None

    def _extract_agent_handle(self, author: str) -> str | None:
        """Extract agent handle from comment author.

        Args:
            author: GitHub username

        Returns:
            Agent handle if recognized, None otherwise
        """
        # Check if author matches known agents
        settings = get_settings()
        all_handles = settings.get_all_agent_handles()

        # Common pattern: viollet-le-duc[bot] -> duc
        author_lower = author.lower().replace("[bot]", "").strip()

        for handle in all_handles:
            if handle in author_lower or author_lower in handle:
                return handle

        return None

    def _extract_summary(self, comment_body: str) -> str:
        """Extract summary from completion comment.

        Args:
            comment_body: Full comment body

        Returns:
            Extracted summary or first line
        """
        # Look for summary after completion marker
        lines = comment_body.split("\n")

        summary_lines = []
        capture = False

        for line in lines:
            # Start capturing after completion marker
            if self.COMPLETION_MARKER in line:
                capture = True
                # Include text after marker on same line
                after_marker = line.split(self.COMPLETION_MARKER, 1)[1].strip()
                if after_marker:
                    summary_lines.append(after_marker)
                continue

            # Stop at artifacts or other sections
            if capture and line.strip().startswith("**"):
                break

            # Capture summary lines
            if capture and line.strip():
                summary_lines.append(line.strip())

        if summary_lines:
            return " ".join(summary_lines)

        # Fallback: return first non-empty line
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped

        return "Task completed"
