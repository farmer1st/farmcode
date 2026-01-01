"""Issue tracker adapters for platform-agnostic operations."""

from farmcode.adapters.base import Comment, IssueContext, IssueTrackerAdapter
from farmcode.adapters.github_adapter import GitHubAdapter

__all__ = ["Comment", "IssueContext", "IssueTrackerAdapter", "GitHubAdapter"]
