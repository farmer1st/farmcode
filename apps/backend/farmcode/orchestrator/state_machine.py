"""State machine for workflow phase transitions."""

from __future__ import annotations

from farmcode.models.phase import WorkflowPhase
from farmcode.models.state import FeatureState


class StateMachine:
    """Manages state transitions through the 8-phase workflow."""

    def __init__(self, state: FeatureState):
        """Initialize state machine with feature state.

        Args:
            state: Feature state to manage
        """
        self.state = state

    def can_advance(self) -> bool:
        """Check if the feature can advance to the next phase.

        For work phases: All assigned agents must be complete.
        For gate phases: Human approval is required.

        Returns:
            True if can advance to next phase
        """
        current_phase_state = self.state.get_current_phase_state()

        if current_phase_state is None:
            return False

        # For gate phases, check if approved
        if self.state.current_phase.is_gate():
            return current_phase_state.human_approved

        # For work phases, check if all agents are complete
        return self.state.all_agents_complete()

    def advance(self) -> bool:
        """Transition to the next phase.

        Returns:
            True if advanced successfully, False if cannot advance

        Raises:
            ValueError: If already at final phase
        """
        if not self.can_advance():
            return False

        next_phase = self.state.current_phase.next_phase()

        if next_phase is None:
            msg = f"Cannot advance from final phase: {self.state.current_phase}"
            raise ValueError(msg)

        # Use the state's advance method
        return self.state.advance()

    def handle_agent_complete(self, agent_handle: str) -> bool:
        """Mark an agent as complete for the current phase.

        Args:
            agent_handle: Handle of the agent that completed (e.g., "duc")

        Returns:
            True if agent was marked complete, False if not in current phase
        """
        # Verify agent is assigned to current phase
        active_agents = self.state.current_phase.get_active_agents()

        if agent_handle not in active_agents:
            return False

        # Mark agent complete
        self.state.mark_agent_complete(agent_handle)
        return True

    def handle_human_approval(self) -> bool:
        """Handle human approval for a gate phase.

        Returns:
            True if approval recorded, False if not at a gate phase

        Raises:
            ValueError: If current phase is not a gate
        """
        if not self.state.current_phase.is_gate():
            msg = f"Cannot approve non-gate phase: {self.state.current_phase}"
            raise ValueError(msg)

        current_phase_state = self.state.get_current_phase_state()

        if current_phase_state is None:
            return False

        # Mark as approved (use the state's approve_gate method)
        self.state.approve_gate()
        return True

    def get_status_summary(self) -> dict:
        """Get a summary of the current state.

        Returns:
            Dictionary with status information
        """
        current_phase_state = self.state.get_current_phase_state()

        if current_phase_state is None:
            return {
                "phase": self.state.current_phase.value,
                "can_advance": False,
                "agents": [],
            }

        agents_status = []
        if not self.state.current_phase.is_gate():
            for agent in self.state.current_phase.get_active_agents():
                # Check if agent is in active_agents dict and if completed
                agent_completion = current_phase_state.active_agents.get(agent)
                is_complete = agent_completion.completed if agent_completion else False
                agents_status.append(
                    {
                        "handle": agent,
                        "complete": is_complete,
                    }
                )

        return {
            "phase": self.state.current_phase.value,
            "is_gate": self.state.current_phase.is_gate(),
            "can_advance": self.can_advance(),
            "agents": agents_status,
            "approved": current_phase_state.human_approved if self.state.current_phase.is_gate() else None,
        }
