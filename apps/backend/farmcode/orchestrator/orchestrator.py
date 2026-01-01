"""Main orchestrator that coordinates all workflow phases."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from farmcode.models.phase import WorkflowPhase
from farmcode.models.state import FeatureState
from farmcode.orchestrator.agent_dispatcher import AgentDispatcher
from farmcode.orchestrator.github_poller import GitHubPoller
from farmcode.orchestrator.phase_manager import PhaseManager
from farmcode.orchestrator.state_machine import StateMachine
from farmcode.storage.state_store import StateStore


class Orchestrator:
    """Main orchestrator for Farm Code workflow management."""

    def __init__(
        self,
        phase_manager: PhaseManager | None = None,
        agent_dispatcher: AgentDispatcher | None = None,
        github_poller: GitHubPoller | None = None,
        state_store: StateStore | None = None,
        poll_interval: int = 10,
    ):
        """Initialize orchestrator.

        Args:
            phase_manager: Phase manager for executing workflow phases
            agent_dispatcher: Agent dispatcher for spawning Claude CLI agents
            github_poller: GitHub poller for monitoring comments
            state_store: State store for persistence
            poll_interval: GitHub polling interval in seconds
        """
        self.phase_manager = phase_manager or PhaseManager()
        self.agent_dispatcher = agent_dispatcher or AgentDispatcher()
        self.github_poller = github_poller or GitHubPoller()
        self.state_store = state_store or StateStore()
        self.poll_interval = poll_interval

        # Track last poll time per issue
        self.last_poll: dict[int, datetime] = {}

    def create_feature(self, title: str, description: str) -> FeatureState:
        """Create a new feature and initialize Phase 1.

        Args:
            title: Feature title
            description: Feature description

        Returns:
            Initialized feature state
        """
        # Execute Phase 1: Create issue, branch, worktree
        state = self.phase_manager.execute_phase_1(title, description)

        # Save state
        self.state_store.save(state)

        # Automatically advance to Phase 2
        self._advance_to_next_phase(state)

        return state

    def _advance_to_next_phase(self, state: FeatureState) -> bool:
        """Advance feature to next phase if possible.

        Args:
            state: Feature state

        Returns:
            True if advanced, False otherwise
        """
        # Create state machine
        machine = StateMachine(state)

        # Check if can advance
        if not machine.can_advance():
            return False

        # Advance
        if not machine.advance():
            return False

        # Save updated state
        self.state_store.save(state)

        # Execute new phase
        self._execute_current_phase(state)

        return True

    def _execute_current_phase(self, state: FeatureState) -> None:
        """Execute the current phase.

        Args:
            state: Feature state
        """
        if state.current_phase == WorkflowPhase.PHASE_2_SPECS:
            # Execute Phase 2: Post comment for @duc
            self.phase_manager.execute_phase_2(state)

            # Dispatch @duc agent
            self.agent_dispatcher.dispatch(
                agent_handle="duc",
                issue_number=state.issue_number,
                worktree_path=state.worktree_path,
                phase=state.current_phase,
            )

        elif state.current_phase == WorkflowPhase.GATE_1_SPECS:
            # Execute Gate 1: Request approval
            self.phase_manager.execute_gate_1(state)

    async def poll_for_updates(self) -> list[dict]:
        """Poll GitHub for updates on all active features.

        Returns:
            List of update events
        """
        updates = []

        # Get all active features
        active_features = self.state_store.list_all()

        for state in active_features:
            issue_number = state.issue_number
            last_check = self.last_poll.get(issue_number)

            # Poll for agent completions
            completions = self.github_poller.poll_for_completions(
                issue_number=issue_number,
                last_check=last_check,
            )

            for completion in completions:
                # Handle agent completion
                machine = StateMachine(state)
                if machine.handle_agent_complete(completion.agent_handle):
                    # Remove agent session
                    self.agent_dispatcher.remove_session(
                        completion.agent_handle,
                        issue_number,
                    )

                    # Save state
                    self.state_store.save(state)

                    # Try to advance
                    if self._advance_to_next_phase(state):
                        updates.append(
                            {
                                "type": "phase_advanced",
                                "issue_number": issue_number,
                                "phase": state.current_phase.value,
                            }
                        )

                    updates.append(
                        {
                            "type": "agent_complete",
                            "issue_number": issue_number,
                            "agent_handle": completion.agent_handle,
                            "summary": completion.summary,
                        }
                    )

            # Poll for human approvals (only for gate phases)
            if state.current_phase.is_gate():
                approval = self.github_poller.poll_for_approval(
                    issue_number=issue_number,
                    last_check=last_check,
                )

                if approval:
                    # Handle approval
                    machine = StateMachine(state)
                    machine.handle_human_approval()

                    # Save state
                    self.state_store.save(state)

                    # Try to advance
                    if self._advance_to_next_phase(state):
                        updates.append(
                            {
                                "type": "phase_advanced",
                                "issue_number": issue_number,
                                "phase": state.current_phase.value,
                            }
                        )

                    updates.append(
                        {
                            "type": "human_approval",
                            "issue_number": issue_number,
                            "approver": approval.approver,
                        }
                    )

            # Update last poll time
            self.last_poll[issue_number] = datetime.now()

        return updates

    async def run_polling_loop(self) -> None:
        """Run continuous polling loop for GitHub updates."""
        while True:
            try:
                updates = await self.poll_for_updates()

                # Log updates (could emit events to frontend here)
                for update in updates:
                    print(f"Update: {update}")

            except Exception as e:
                print(f"Polling error: {e}")

            # Wait before next poll
            await asyncio.sleep(self.poll_interval)

    def approve_gate(self, issue_number: int) -> bool:
        """Manually approve a gate phase.

        Args:
            issue_number: GitHub issue number

        Returns:
            True if approved and advanced, False otherwise
        """
        # Load state
        state = self.state_store.load(issue_number)

        if state is None:
            return False

        # Verify at gate
        if not state.current_phase.is_gate():
            return False

        # Mark approved
        machine = StateMachine(state)
        machine.handle_human_approval()

        # Save state
        self.state_store.save(state)

        # Advance to next phase
        return self._advance_to_next_phase(state)

    def get_feature_state(self, issue_number: int) -> FeatureState | None:
        """Get current state of a feature.

        Args:
            issue_number: GitHub issue number

        Returns:
            Feature state if exists, None otherwise
        """
        return self.state_store.load(issue_number)

    def list_all_features(self) -> list[FeatureState]:
        """List all active features.

        Returns:
            List of all feature states
        """
        return self.state_store.list_all()
