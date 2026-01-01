"""Git worktree management for isolated feature development."""

from __future__ import annotations

import re
from pathlib import Path

from git import Repo
from pydantic import BaseModel

from farmcode.config import get_settings


class WorktreeInfo(BaseModel):
    """Information about a created worktree."""

    issue_number: int
    branch_name: str
    worktree_path: Path


class WorktreeManager:
    """Manages git worktrees for feature isolation."""

    def __init__(self, main_repo_path: Path | None = None):
        """Initialize worktree manager.

        Args:
            main_repo_path: Path to main repository. If None, derives from settings.
        """
        settings = get_settings()

        if main_repo_path is None:
            # Default to worktree_base parent (assumes main repo is sibling)
            repo_name = settings.repository.main.split("/")[1]
            main_repo_path = settings.paths.worktree_base / repo_name

        self.main_repo_path = main_repo_path
        self.worktree_base = settings.paths.worktree_base
        self.repo = Repo(str(main_repo_path))

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Lowercase slug with hyphens
        """
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Strip leading/trailing hyphens
        return slug.strip("-")

    def _create_plans_structure(
        self,
        worktree_path: Path,
        issue_number: int,
        title: str,
    ) -> None:
        """Create .plans/ folder structure in worktree.

        Args:
            worktree_path: Path to worktree
            issue_number: GitHub issue number
            title: Feature title
        """
        plans_dir = worktree_path / ".plans" / str(issue_number)

        # Create subdirectories
        (plans_dir / "specs").mkdir(parents=True, exist_ok=True)
        (plans_dir / "plans").mkdir(parents=True, exist_ok=True)
        (plans_dir / "reviews").mkdir(parents=True, exist_ok=True)
        (plans_dir / "qa").mkdir(parents=True, exist_ok=True)

        # Create README.md
        readme_content = self._readme_template(issue_number, title)
        readme_path = plans_dir / "README.md"
        readme_path.write_text(readme_content)

    def _readme_template(self, issue_number: int, title: str) -> str:
        """Generate README.md template for .plans/ folder.

        Args:
            issue_number: GitHub issue number
            title: Feature title

        Returns:
            README content
        """
        settings = get_settings()
        repo_full_name = settings.repository.main

        return f"""# Feature #{issue_number}: {title}

This folder contains all planning artifacts for this feature.

## Folder Structure

- `specs/` - Architecture specifications from @duc
- `plans/` - Implementation plans from @baron
- `reviews/` - Code review feedback from @dede
- `qa/` - Test plans and results from @marie

## GitHub Issue

[#{issue_number}](https://github.com/{repo_full_name}/issues/{issue_number})

## Workflow Status

Track progress in the GitHub issue comments.
"""

    def create_worktree(self, issue_number: int, title: str) -> WorktreeInfo:
        """Create git branch and worktree for a feature.

        Args:
            issue_number: GitHub issue number
            title: Feature title

        Returns:
            WorktreeInfo with branch name and worktree path

        Raises:
            ValueError: If branch or worktree already exists
        """
        # Derive branch name
        slug = self._slugify(title)
        branch_name = f"{issue_number}-{slug}"

        # Check if branch exists
        if branch_name in [ref.name for ref in self.repo.references]:
            msg = f"Branch '{branch_name}' already exists"
            raise ValueError(msg)

        # Check if worktree path exists
        worktree_path = self.worktree_base / branch_name
        if worktree_path.exists():
            msg = f"Worktree path '{worktree_path}' already exists"
            raise ValueError(msg)

        # Create branch from main
        main_branch = self.repo.heads.main
        new_branch = self.repo.create_head(branch_name, main_branch)

        # Create worktree
        self.repo.git.worktree("add", str(worktree_path), branch_name)

        # Create .plans/ structure
        self._create_plans_structure(worktree_path, issue_number, title)

        # Commit and push .plans/ folder
        worktree_repo = Repo(str(worktree_path))
        worktree_repo.index.add([".plans/"])
        worktree_repo.index.commit(f"chore({issue_number}): initialize plans folder")

        # Push branch to remote
        origin = worktree_repo.remote("origin")
        origin.push(refspec=f"{branch_name}:{branch_name}", set_upstream=True)

        return WorktreeInfo(
            issue_number=issue_number,
            branch_name=branch_name,
            worktree_path=worktree_path,
        )

    def delete_worktree(self, branch_name: str) -> None:
        """Remove worktree and delete local branch.

        Args:
            branch_name: Name of branch to clean up

        Raises:
            ValueError: If worktree doesn't exist
        """
        worktree_path = self.worktree_base / branch_name

        if not worktree_path.exists():
            msg = f"Worktree '{worktree_path}' does not exist"
            raise ValueError(msg)

        # Remove worktree
        self.repo.git.worktree("remove", str(worktree_path))

        # Delete local branch
        self.repo.delete_head(branch_name, force=True)

    def worktree_exists(self, branch_name: str) -> bool:
        """Check if worktree exists for a branch.

        Args:
            branch_name: Branch name to check

        Returns:
            True if worktree exists
        """
        worktree_path = self.worktree_base / branch_name
        return worktree_path.exists()
