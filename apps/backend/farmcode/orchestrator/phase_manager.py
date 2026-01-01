"""Phase execution manager for the workflow."""

from __future__ import annotations

from pathlib import Path

from farmcode.adapters.github_adapter import GitHubAdapter
from farmcode.config import get_settings
from farmcode.git.worktree_manager import WorktreeManager
from farmcode.models.phase import WorkflowPhase
from farmcode.models.state import FeatureState


class PhaseManager:
    """Executes workflow phases and manages transitions."""

    def __init__(
        self,
        worktree_manager: WorktreeManager | None = None,
        github_adapter: GitHubAdapter | None = None,
    ):
        """Initialize phase manager.

        Args:
            worktree_manager: Git worktree manager. If None, creates default.
            github_adapter: GitHub adapter. If None, creates default with "orchestrator" handle.
        """
        settings = get_settings()

        self.worktree_manager = worktree_manager or WorktreeManager()

        # Use "orchestrator" as the agent handle for system operations
        self.github_adapter = github_adapter or GitHubAdapter(
            repo=settings.repository.main,
            agent_handle="orchestrator",
        )

    def execute_phase_1(self, title: str, description: str) -> FeatureState:
        """Execute Phase 1: Create issue, branch, worktree, and .plans/ folder.

        Args:
            title: Feature title
            description: Feature description

        Returns:
            Initialized feature state

        Raises:
            ValueError: If issue creation or worktree creation fails
        """
        # Create GitHub issue
        issue_context = self.github_adapter.create_issue(
            title=title,
            body=description,
            labels=["farmcode", WorkflowPhase.PHASE_1_SETUP.get_github_label()],
        )

        issue_number = int(issue_context.issue_id)

        # Create worktree
        worktree_info = self.worktree_manager.create_worktree(
            issue_number=issue_number,
            title=title,
        )

        # Initialize feature state
        state = FeatureState(
            issue_number=issue_number,
            title=title,
            description=description,
            branch_name=worktree_info.branch_name,
            worktree_path=worktree_info.worktree_path,
            current_phase=WorkflowPhase.PHASE_1_SETUP,
            phase_history=[],
        )

        # Start Phase 1 (marks as complete immediately since it's synchronous)
        state.start_phase(WorkflowPhase.PHASE_1_SETUP)
        # Phase 1 has no agents, so mark as complete immediately
        state.get_current_phase_state().approved = True

        # Post initial comment
        self.github_adapter.post_comment(
            issue_id=str(issue_number),
            body=f"""🚀 Farm Code initialized this feature!

**Branch**: `{worktree_info.branch_name}`
**Worktree**: `{worktree_info.worktree_path}`

Phase 1 (Setup) complete. Ready to advance to Phase 2 (Specs).
""",
        )

        return state

    def execute_phase_2(self, state: FeatureState) -> None:
        """Execute Phase 2: Dispatch @duc to write architecture specs.

        Args:
            state: Feature state

        Note:
            This method initiates agent dispatch. Actual completion is tracked
            via GitHub comment polling.
        """
        # Verify we're in the right phase
        if state.current_phase != WorkflowPhase.PHASE_2_SPECS:
            msg = f"Cannot execute Phase 2 from {state.current_phase}"
            raise ValueError(msg)

        # Post comment to trigger @duc
        self.github_adapter.post_comment(
            issue_id=str(state.issue_number),
            body=f"""📋 **Phase 2: Architecture Specs**

@duc - Please analyze this feature and write architecture specifications.

**Task**:
- Review the feature requirements
- Design the system architecture
- Document specs in `.plans/{state.issue_number}/specs/`
- Post ✅ when complete

**Context**:
- Branch: `{state.branch_name}`
- Worktree: `{state.worktree_path}`
""",
        )

        # Note: Agent dispatch will happen via the orchestrator's agent dispatcher
        # This method just sets up the phase and posts the initial comment

    def execute_gate_1(self, state: FeatureState) -> None:
        """Execute Gate 1: Wait for human approval of specs.

        Args:
            state: Feature state

        Note:
            This method posts the approval request. Actual approval is tracked
            via GitHub comment polling.
        """
        # Verify we're in the right phase
        if state.current_phase != WorkflowPhase.GATE_1_SPECS:
            msg = f"Cannot execute Gate 1 from {state.current_phase}"
            raise ValueError(msg)

        # Post comment requesting approval
        self.github_adapter.post_comment(
            issue_id=str(state.issue_number),
            body=f"""⏸️ **Gate 1: Spec Approval Required**

@duc has completed the architecture specifications. Please review:

📁 Specs location: `.plans/{state.issue_number}/specs/`

**To approve and proceed to Phase 3:**
- Comment: `approved` or `lgtm`
- Or use the Farm Code UI approval button

**To request changes:**
- Comment with feedback
- @duc will revise
""",
        )
