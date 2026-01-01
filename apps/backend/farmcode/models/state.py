"""Feature state tracking for the workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from farmcode.models.phase import WorkflowPhase


class AgentCompletion(BaseModel):
    """Tracks completion status of an agent in a phase."""

    agent_handle: str
    completed: bool = False
    completed_at: datetime | None = None
    artifact_path: str | None = None
    comment_id: str | None = None


class PhaseState(BaseModel):
    """State tracking for a single phase."""

    phase: WorkflowPhase
    started_at: datetime | None = None
    completed_at: datetime | None = None
    active_agents: dict[str, AgentCompletion] = Field(default_factory=dict)
    human_approved: bool = False
    human_approved_at: datetime | None = None


class FeatureState(BaseModel):
    """Complete state tracking for a feature going through the workflow."""

    # GitHub Issue Info
    issue_number: int
    title: str
    description: str

    # Git Info
    branch_name: str
    worktree_path: Path
    pr_number: int | None = None

    # Workflow State
    current_phase: WorkflowPhase = WorkflowPhase.PHASE_1_SETUP
    phase_history: list[PhaseState] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    def start_phase(self, phase: WorkflowPhase) -> None:
        """Transition to a new phase."""
        # Complete previous phase if exists
        if self.phase_history:
            self.phase_history[-1].completed_at = datetime.now(UTC)

        # Start new phase
        phase_state = PhaseState(
            phase=phase,
            started_at=datetime.now(UTC),
        )

        # Initialize active agents for this phase
        for agent_handle in phase.get_active_agents():
            phase_state.active_agents[agent_handle] = AgentCompletion(agent_handle=agent_handle)

        self.phase_history.append(phase_state)
        self.current_phase = phase
        self.updated_at = datetime.now(UTC)

    def get_current_phase_state(self) -> PhaseState | None:
        """Get the state object for the current phase."""
        if not self.phase_history:
            return None
        return self.phase_history[-1]

    def mark_agent_complete(
        self,
        agent_handle: str,
        artifact_path: str | None = None,
        comment_id: str | None = None,
    ) -> None:
        """Mark an agent as complete in the current phase."""
        phase_state = self.get_current_phase_state()
        if not phase_state:
            return

        if agent_handle in phase_state.active_agents:
            phase_state.active_agents[agent_handle].completed = True
            phase_state.active_agents[agent_handle].completed_at = datetime.now(UTC)
            phase_state.active_agents[agent_handle].artifact_path = artifact_path
            phase_state.active_agents[agent_handle].comment_id = comment_id
            self.updated_at = datetime.now(UTC)

    def all_agents_complete(self) -> bool:
        """Check if all agents in the current phase are complete."""
        phase_state = self.get_current_phase_state()
        if not phase_state or not phase_state.active_agents:
            return True  # No agents = auto complete

        return all(agent.completed for agent in phase_state.active_agents.values())

    def approve_gate(self) -> None:
        """Approve the current gate (human approval)."""
        phase_state = self.get_current_phase_state()
        if phase_state:
            phase_state.human_approved = True
            phase_state.human_approved_at = datetime.now(UTC)
            self.updated_at = datetime.now(UTC)

    def can_advance(self) -> bool:
        """Check if the workflow can advance to the next phase."""
        if self.current_phase.is_terminal():
            return False

        # Gates require human approval
        if self.current_phase.is_gate():
            phase_state = self.get_current_phase_state()
            return phase_state.human_approved if phase_state else False

        # Non-gate phases require all agents to complete
        return self.all_agents_complete()

    def advance(self) -> bool:
        """Advance to the next phase if possible."""
        if not self.can_advance():
            return False

        next_phase = self.current_phase.next_phase()
        if next_phase is None:
            return False

        self.start_phase(next_phase)
        return True

    def get_pending_agents(self) -> list[str]:
        """Get list of agents that haven't completed in the current phase."""
        phase_state = self.get_current_phase_state()
        if not phase_state:
            return []

        return [
            agent.agent_handle
            for agent in phase_state.active_agents.values()
            if not agent.completed
        ]

    def get_completed_agents(self) -> list[str]:
        """Get list of agents that have completed in the current phase."""
        phase_state = self.get_current_phase_state()
        if not phase_state:
            return []

        return [
            agent.agent_handle
            for agent in phase_state.active_agents.values()
            if agent.completed
        ]

    def get_github_label(self) -> str:
        """Get the current GitHub label based on phase."""
        return self.current_phase.get_github_label()
