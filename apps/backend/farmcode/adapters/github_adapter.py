"""GitHub adapter using gh CLI via gh-agent wrapper."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from farmcode.adapters.base import Comment, IssueContext, IssueTrackerAdapter


class GitHubAdapter:
    """GitHub issue tracker adapter using gh CLI with gh-agent wrapper.

    Uses the existing gh-agent script from farmer1st-developer-toolkit
    to authenticate as different agents via GitHub Apps.
    """

    def __init__(
        self,
        repo: str,
        agent_handle: str,
        gh_agent_path: Path | None = None,
        worktree_base_path: Path | None = None,
        keys_dir: Path | None = None,
    ) -> None:
        """Initialize GitHub adapter.

        Args:
            repo: Repository in format "owner/repo" (e.g., "farmer1st/platform")
            agent_handle: Agent handle (e.g., "duc", "dede", "baron")
            gh_agent_path: Path to gh-agent script (defaults to toolkit utilities/gh-agent)
            worktree_base_path: Base path for worktrees (for reading specs/plans)
            keys_dir: Path to .keys directory (defaults to ~/Dev/farmer1st/github/.keys)
        """
        self.repo = repo
        self.agent_handle = agent_handle

        # Default to toolkit's gh-agent script
        if gh_agent_path is None:
            # Assumes toolkit is a sibling of farmcode repo
            toolkit_path = Path(__file__).parent.parent.parent.parent.parent.parent
            gh_agent_path = (
                toolkit_path / "farmer1st-developer-toolkit" / "utilities" / "gh-agent"
            )

        if not gh_agent_path.exists():
            msg = f"gh-agent script not found at {gh_agent_path}"
            raise FileNotFoundError(msg)

        self.gh_agent_path = gh_agent_path

        # Default paths
        github_base = Path.home() / "Dev" / "farmer1st" / "github"
        self.worktree_base_path = worktree_base_path or github_base
        self.keys_dir = keys_dir or (github_base / ".keys")

        # Verify agent key exists
        agent_key = self.keys_dir / f"{agent_handle}.pem"
        if not agent_key.exists():
            msg = f"Agent key not found: {agent_key}"
            raise FileNotFoundError(msg)

    def _run_gh(self, *args: str) -> str:
        """Run gh CLI command as the configured agent.

        Returns stdout as string.
        Raises subprocess.CalledProcessError on failure.
        """
        cmd = [str(self.gh_agent_path), self.agent_handle, *args]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def _get_worktree_path(self, issue_number: int) -> Path | None:
        """Get worktree path for an issue by reading issue body or branch."""
        try:
            # Get issue details
            issue_json = self._run_gh(
                "issue", "view", str(issue_number), "--repo", self.repo, "--json", "title"
            )
            issue_data = json.loads(issue_json)
            title = issue_data.get("title", "")

            # Derive branch name (same as orchestrator logic)
            slug = self._slugify(title)
            branch_name = f"{issue_number}-{slug}"
            worktree_path = self.worktree_base_path / branch_name

            if worktree_path.exists():
                return worktree_path

        except Exception:
            pass

        return None

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug (lowercase, alphanumeric + hyphens)."""
        import re

        # Lowercase
        slug = text.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Keep only alphanumeric and hyphens
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        # Remove consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        # Limit to 50 chars
        return slug[:50]

    def _read_plans_folder(self, worktree_path: Path, issue_number: int) -> dict:
        """Read specs and plans from .plans/{issue}/ folder."""
        plans_dir = worktree_path / ".plans" / str(issue_number)
        specs_dir = plans_dir / "specs"

        specs = []
        plans = []

        # Read specs
        if specs_dir.exists():
            for spec_file in specs_dir.glob("*.md"):
                specs.append({"path": str(spec_file.relative_to(worktree_path)), "content": spec_file.read_text()})

        # Read plans (top-level .md files excluding README.md)
        if plans_dir.exists():
            for plan_file in plans_dir.glob("*.md"):
                if plan_file.name.lower() != "readme.md":
                    plans.append({
                        "path": str(plan_file.relative_to(worktree_path)),
                        "content": plan_file.read_text(),
                    })

        return {"specs": specs, "plans": plans}

    def get_issue_context(self, issue_id: str) -> IssueContext:
        """Get complete context for a GitHub issue."""
        issue_number = int(issue_id)

        # Get issue details via gh CLI JSON output
        issue_json = self._run_gh(
            "issue",
            "view",
            str(issue_number),
            "--repo",
            self.repo,
            "--json",
            "number,title,body,labels",
        )

        issue_data = json.loads(issue_json)

        # Get comments
        comments_json = self._run_gh(
            "issue",
            "view",
            str(issue_number),
            "--repo",
            self.repo,
            "--json",
            "comments",
        )

        comments_data = json.loads(comments_json)
        comments = [
            Comment(
                id=str(c.get("id", "")),
                author=c.get("author", {}).get("login", "unknown"),
                created_at=datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00")),
                body=c.get("body", ""),
            )
            for c in comments_data.get("comments", [])
        ]

        # Get worktree path and read specs/plans
        worktree_path = self._get_worktree_path(issue_number)
        specs = []
        plans = []

        if worktree_path:
            plans_data = self._read_plans_folder(worktree_path, issue_number)
            specs = plans_data["specs"]
            plans = plans_data["plans"]

        # Determine phase from labels
        labels = [label["name"] for label in issue_data.get("labels", [])]
        phase = None
        for label in labels:
            if label.startswith("status:"):
                phase = label
                break

        return IssueContext(
            issue_number=issue_number,
            title=issue_data["title"],
            body=issue_data.get("body", ""),
            labels=labels,
            phase=phase,
            worktree_path=worktree_path,
            specs=specs,
            plans=plans,
            comments=comments,
        )

    def post_comment(self, issue_id: str, body: str) -> str:
        """Post a comment on a GitHub issue as the configured agent."""
        # Use gh issue comment
        result = self._run_gh(
            "issue", "comment", issue_id, "--repo", self.repo, "--body", body
        )

        # Extract comment URL from output (gh prints the URL)
        # Format: https://github.com/owner/repo/issues/123#issuecomment-456789
        if "#issuecomment-" in result:
            comment_id = result.split("#issuecomment-")[-1].strip()
            return comment_id

        return "unknown"

    def add_label(self, issue_id: str, label: str) -> None:
        """Add a label to a GitHub issue."""
        self._run_gh(
            "issue", "edit", issue_id, "--repo", self.repo, "--add-label", label
        )

    def remove_label(self, issue_id: str, label: str) -> None:
        """Remove a label from a GitHub issue."""
        self._run_gh(
            "issue", "edit", issue_id, "--repo", self.repo, "--remove-label", label
        )

    def get_comments(
        self,
        issue_id: str,
        since: datetime | None = None,
        from_author: str | None = None,
    ) -> list[Comment]:
        """Get comments on a GitHub issue, optionally filtered."""
        comments_json = self._run_gh(
            "issue",
            "view",
            issue_id,
            "--repo",
            self.repo,
            "--json",
            "comments",
        )

        comments_data = json.loads(comments_json)
        comments = [
            Comment(
                id=str(c.get("id", "")),
                author=c.get("author", {}).get("login", "unknown"),
                created_at=datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00")),
                body=c.get("body", ""),
            )
            for c in comments_data.get("comments", [])
        ]

        # Apply filters
        if since:
            comments = [c for c in comments if c.created_at >= since]

        if from_author:
            comments = [c for c in comments if c.author == from_author]

        return comments

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> str:
        """Create a new GitHub issue."""
        args = ["issue", "create", "--repo", self.repo, "--title", title, "--body", body]

        if labels:
            args.extend(["--label", ",".join(labels)])

        result = self._run_gh(*args)

        # gh issue create returns the issue URL
        # Format: https://github.com/owner/repo/issues/123
        if "/issues/" in result:
            issue_number = result.split("/issues/")[-1].strip()
            return issue_number

        return "unknown"

    def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        body: str | None = None,
    ) -> None:
        """Update a GitHub issue's title or body."""
        args = ["issue", "edit", issue_id, "--repo", self.repo]

        if title:
            args.extend(["--title", title])

        if body:
            args.extend(["--body", body])

        self._run_gh(*args)

    def close_issue(self, issue_id: str, comment: str | None = None) -> None:
        """Close a GitHub issue with an optional comment."""
        if comment:
            self.post_comment(issue_id, comment)

        self._run_gh("issue", "close", issue_id, "--repo", self.repo)
