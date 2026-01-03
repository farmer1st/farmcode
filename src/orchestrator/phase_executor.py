"""Phase Executor for orchestrator workflow phases.

This module handles the execution of SDLC workflow phases,
including Phase 1 (Issue Setup) and Phase 2 (Specification).
"""

import re
import time
from pathlib import Path
from typing import Any

from orchestrator.errors import (
    BranchCreationError,
    IssueCreationError,
    PlansInitializationError,
    WorktreeCreationError,
)
from orchestrator.logger import logger
from orchestrator.models import (
    OrchestratorState,
    Phase1Request,
    PhaseResult,
)


def _slugify(text: str) -> str:
    """Convert text to a kebab-case slug.

    Args:
        text: Text to convert.

    Returns:
        Kebab-case slug suitable for branch names.
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Remove consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Trim hyphens from ends
    text = text.strip("-")
    # Limit length
    return text[:50]


class PhaseExecutor:
    """Executes workflow phases with step tracking.

    The PhaseExecutor manages the execution of Phase 1 and Phase 2,
    tracking which steps have been completed to allow for resumable
    execution after failures.

    Attributes:
        _repo_path: Path to the repository root.
        _github: GitHub service for API operations.
        _worktree: Worktree service for git operations.
        _state_machine: State machine for workflow state.

    Example:
        >>> executor = PhaseExecutor(Path("/repo"), github, worktree, state_machine)
        >>> result = executor.execute_phase_1(Phase1Request(
        ...     feature_description="Add user auth"
        ... ))
    """

    def __init__(
        self,
        repo_path: Path,
        github_service: Any,  # GitHubService type
        worktree_service: Any,  # WorktreeService type
        state_machine: Any,  # StateMachine type
    ) -> None:
        """Initialize the phase executor.

        Args:
            repo_path: Path to the repository root.
            github_service: GitHub service for API operations.
            worktree_service: Worktree service for git operations.
            state_machine: State machine for workflow state.
        """
        self._repo_path = repo_path
        self._github = github_service
        self._worktree = worktree_service
        self._state_machine = state_machine

    def execute_phase_1(self, request: Phase1Request) -> PhaseResult:
        """Execute Phase 1: Issue Setup.

        Creates GitHub issue, branch, worktree, and .plans structure.
        Supports resumable execution if interrupted.

        Args:
            request: Phase 1 configuration.

        Returns:
            PhaseResult with created artifacts.

        Raises:
            IssueCreationError: If GitHub issue creation fails.
            BranchCreationError: If branch creation fails.
            WorktreeCreationError: If worktree creation fails.
            PlansInitializationError: If .plans setup fails.
        """
        start_time = time.time()
        artifacts: list[str] = []
        steps_completed: list[str] = []

        # Derive feature name if not provided
        feature_name = request.feature_name or _slugify(request.feature_description)

        # Get or create state
        state = self._state_machine.get_state(0)  # Will be updated after issue creation

        try:
            # Step 1: Create GitHub issue
            if not state or "issue" not in (state.phase1_steps or []):
                issue_result = self._create_issue(
                    request.feature_description,
                    request.labels,
                )
                issue_number = issue_result["number"]
                artifacts.append(f"issue#{issue_number}")
                steps_completed.append("issue")

                # Create state for this issue
                self._state_machine.create_state(
                    issue_number=issue_number,
                    feature_name=feature_name,
                )
                # Transition to PHASE_1
                self._state_machine.transition(issue_number, "phase_1_start")

                # Reload state after transition to get updated current_state
                state = self._state_machine.get_state(issue_number)
                # Update state with step completion
                state.phase1_steps.append("issue")
                self._state_machine._save_state(state)

                logger.info(
                    f"Created issue #{issue_number}",
                    extra={"context": {"issue_number": issue_number}},
                )
            else:
                issue_number = state.issue_number

            # Refresh state
            state = self._state_machine.get_state(issue_number)

            # Step 2: Create branch
            if "branch" not in state.phase1_steps:
                branch_result = self._create_branch(issue_number, feature_name)
                branch_name = branch_result["name"]
                artifacts.append(f"branch:{branch_name}")
                steps_completed.append("branch")

                # Update state
                state.branch_name = branch_name
                state.phase1_steps.append("branch")
                self._state_machine._save_state(state)

                logger.info(
                    f"Created branch {branch_name}",
                    extra={"context": {"branch_name": branch_name}},
                )
            else:
                branch_name = state.branch_name

            # Step 3: Create worktree
            if "worktree" not in state.phase1_steps:
                worktree_result = self._create_worktree(issue_number, branch_name)
                worktree_path = worktree_result["path"]
                artifacts.append(f"worktree:{worktree_path}")
                steps_completed.append("worktree")

                # Update state
                state.worktree_path = worktree_path
                state.phase1_steps.append("worktree")
                self._state_machine._save_state(state)

                logger.info(
                    f"Created worktree at {worktree_path}",
                    extra={"context": {"worktree_path": str(worktree_path)}},
                )
            else:
                worktree_path = state.worktree_path

            # Step 4: Initialize .plans structure
            if "plans" not in state.phase1_steps:
                self._initialize_plans(issue_number, worktree_path)
                artifacts.append(f".plans/{issue_number}/")
                steps_completed.append("plans")

                # Update state
                state.phase1_steps.append("plans")
                self._state_machine._save_state(state)

                logger.info(
                    f"Initialized .plans/{issue_number}/",
                    extra={"context": {"issue_number": issue_number}},
                )

            # Transition to PHASE_2
            self._state_machine.transition(issue_number, "phase_1_complete")

            duration = time.time() - start_time
            return PhaseResult(
                success=True,
                phase="phase_1",
                artifacts_created=artifacts,
                steps_completed=steps_completed,
                duration_seconds=duration,
            )

        except IssueCreationError:
            raise
        except BranchCreationError:
            raise
        except WorktreeCreationError:
            raise
        except PlansInitializationError:
            raise
        except Exception as e:
            logger.error(
                f"Phase 1 failed: {e}",
                extra={"context": {"error": str(e)}},
            )
            raise

    def _create_issue(
        self,
        description: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a GitHub issue.

        Args:
            description: Feature description for issue title/body.
            labels: Optional labels to apply.

        Returns:
            Dict with issue details including 'number'.

        Raises:
            IssueCreationError: If issue creation fails.
        """
        try:
            # Extract title (first line or first 80 chars)
            lines = description.strip().split("\n")
            title = lines[0][:80] if lines else description[:80]

            result = self._github.create_issue(
                title=title,
                body=description,
                labels=labels or [],
            )
            return {"number": result.number, "title": result.title}
        except Exception as e:
            raise IssueCreationError(f"Failed to create issue: {e}") from e

    def _create_branch(
        self,
        issue_number: int,
        feature_name: str,
    ) -> dict[str, Any]:
        """Create a feature branch.

        Args:
            issue_number: GitHub issue number.
            feature_name: Feature slug for branch name.

        Returns:
            Dict with branch details including 'name'.

        Raises:
            BranchCreationError: If branch creation fails.
        """
        try:
            branch_name = f"{issue_number}-{feature_name}"
            result = self._github.create_branch(name=branch_name)
            return {"name": result.name}
        except Exception as e:
            raise BranchCreationError(f"Failed to create branch: {e}") from e

    def _create_worktree(
        self,
        issue_number: int,
        branch_name: str,
    ) -> dict[str, Any]:
        """Create a git worktree.

        Args:
            issue_number: GitHub issue number.
            branch_name: Branch to checkout in worktree.

        Returns:
            Dict with worktree details including 'path'.

        Raises:
            WorktreeCreationError: If worktree creation fails.
        """
        try:
            result = self._worktree.create_worktree(
                issue_number=issue_number,
                branch_name=branch_name,
            )
            return {"path": result.path, "branch": result.branch}
        except Exception as e:
            raise WorktreeCreationError(f"Failed to create worktree: {e}") from e

    def _initialize_plans(
        self,
        issue_number: int,
        worktree_path: Path,
    ) -> dict[str, Any]:
        """Initialize .plans directory structure.

        Creates .plans/{issue_number}/ directory with state.json.

        Args:
            issue_number: GitHub issue number.
            worktree_path: Path to the worktree.

        Returns:
            Dict with initialization status.

        Raises:
            PlansInitializationError: If initialization fails.
        """
        try:
            plans_dir = worktree_path / ".plans" / str(issue_number)
            plans_dir.mkdir(parents=True, exist_ok=True)

            # Create empty state.json placeholder
            state_file = plans_dir / "state.json"
            if not state_file.exists():
                state_file.write_text("{}")

            return {"initialized": True, "path": str(plans_dir)}
        except Exception as e:
            raise PlansInitializationError(f"Failed to initialize .plans: {e}") from e

    def _execute_phase_1_steps(
        self,
        request: Phase1Request,
        state: OrchestratorState,
    ) -> PhaseResult:
        """Execute remaining Phase 1 steps for resumable execution.

        This is a helper method for resuming Phase 1 after partial completion.

        Args:
            request: Phase 1 configuration.
            state: Current workflow state.

        Returns:
            PhaseResult with newly completed steps.
        """
        completed = state.phase1_steps or []
        new_steps: list[str] = []

        # All steps already done
        if len(completed) >= 4:
            return PhaseResult(
                success=True,
                phase="phase_1",
                steps_completed=[],
                duration_seconds=0,
            )

        issue_number = state.issue_number
        feature_name = state.feature_name

        # Execute remaining steps
        if "branch" not in completed and "issue" in completed:
            branch_result = self._create_branch(issue_number, feature_name)
            state.branch_name = branch_result["name"]
            state.phase1_steps.append("branch")
            new_steps.append("branch")
            self._state_machine._save_state(state)

        if "worktree" not in completed and "branch" in state.phase1_steps:
            # branch_name is guaranteed to be set since "branch" step is complete
            assert state.branch_name is not None
            worktree_result = self._create_worktree(
                issue_number,
                state.branch_name,
            )
            state.worktree_path = worktree_result["path"]
            state.phase1_steps.append("worktree")
            new_steps.append("worktree")
            self._state_machine._save_state(state)

        if "plans" not in completed and "worktree" in state.phase1_steps:
            # worktree_path is guaranteed to be set since "worktree" step is complete
            assert state.worktree_path is not None
            self._initialize_plans(issue_number, state.worktree_path)
            state.phase1_steps.append("plans")
            new_steps.append("plans")
            self._state_machine._save_state(state)

        return PhaseResult(
            success=True,
            phase="phase_1",
            steps_completed=new_steps,
            duration_seconds=0,
        )
