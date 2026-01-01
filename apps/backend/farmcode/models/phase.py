"""Workflow phase definitions matching the 8-phase SDLC."""

from enum import Enum


class WorkflowPhase(str, Enum):
    """8-phase SDLC workflow phases."""

    # Phase 1: Issue & Worktree Creation
    PHASE_1_SETUP = "PHASE_1_SETUP"

    # Phase 2: Architecture & Specs
    PHASE_2_SPECS = "PHASE_2_SPECS"

    # Gate 1: Human Approval (Specs)
    GATE_1_SPECS = "GATE_1_SPECS"

    # Phase 3: Implementation Plans
    PHASE_3_PLANS = "PHASE_3_PLANS"

    # Gate 2: Human Approval (Plans)
    GATE_2_PLANS = "GATE_2_PLANS"

    # Phase 4: Test Design
    PHASE_4_TESTS = "PHASE_4_TESTS"

    # Gate 3: Human Approval (Tests)
    GATE_3_TESTS = "GATE_3_TESTS"

    # Phase 5: Implementation (TDD)
    PHASE_5_IMPLEMENTATION = "PHASE_5_IMPLEMENTATION"

    # Phase 6: Create PR
    PHASE_6_CREATE_PR = "PHASE_6_CREATE_PR"

    # Phase 7: Review
    PHASE_7_REVIEW = "PHASE_7_REVIEW"

    # Gate 4: Human Approval (Merge)
    GATE_4_MERGE = "GATE_4_MERGE"

    # Phase 8: Merge & Cleanup
    PHASE_8_CLEANUP = "PHASE_8_CLEANUP"

    # Terminal states
    DONE = "DONE"
    CANCELLED = "CANCELLED"

    def is_gate(self) -> bool:
        """Check if this phase is a human approval gate."""
        return self.name.startswith("GATE_")

    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in (WorkflowPhase.DONE, WorkflowPhase.CANCELLED)

    def next_phase(self) -> "WorkflowPhase | None":
        """Get the next phase in the workflow."""
        phase_sequence = [
            WorkflowPhase.PHASE_1_SETUP,
            WorkflowPhase.PHASE_2_SPECS,
            WorkflowPhase.GATE_1_SPECS,
            WorkflowPhase.PHASE_3_PLANS,
            WorkflowPhase.GATE_2_PLANS,
            WorkflowPhase.PHASE_4_TESTS,
            WorkflowPhase.GATE_3_TESTS,
            WorkflowPhase.PHASE_5_IMPLEMENTATION,
            WorkflowPhase.PHASE_6_CREATE_PR,
            WorkflowPhase.PHASE_7_REVIEW,
            WorkflowPhase.GATE_4_MERGE,
            WorkflowPhase.PHASE_8_CLEANUP,
            WorkflowPhase.DONE,
        ]

        try:
            current_idx = phase_sequence.index(self)
            if current_idx < len(phase_sequence) - 1:
                return phase_sequence[current_idx + 1]
        except ValueError:
            pass

        return None

    def get_github_label(self) -> str:
        """Get the GitHub label for this phase."""
        label_map = {
            WorkflowPhase.PHASE_1_SETUP: "status:new",
            WorkflowPhase.PHASE_2_SPECS: "status:new",
            WorkflowPhase.GATE_1_SPECS: "status:specs-ready",
            WorkflowPhase.PHASE_3_PLANS: "status:specs-ready",
            WorkflowPhase.GATE_2_PLANS: "status:plans-ready",
            WorkflowPhase.PHASE_4_TESTS: "status:plans-ready",
            WorkflowPhase.GATE_3_TESTS: "status:tests-designed",
            WorkflowPhase.PHASE_5_IMPLEMENTATION: "status:implementing",
            WorkflowPhase.PHASE_6_CREATE_PR: "status:implementing",
            WorkflowPhase.PHASE_7_REVIEW: "status:in-review",
            WorkflowPhase.GATE_4_MERGE: "status:approved",
            WorkflowPhase.PHASE_8_CLEANUP: "status:approved",
            WorkflowPhase.DONE: "status:done",
            WorkflowPhase.CANCELLED: "status:cancelled",
        }
        return label_map.get(self, "status:new")

    def get_active_agents(self) -> list[str]:
        """Get the list of agents that should be active in this phase."""
        agent_map = {
            WorkflowPhase.PHASE_1_SETUP: [],  # Program executes
            WorkflowPhase.PHASE_2_SPECS: ["duc"],
            WorkflowPhase.GATE_1_SPECS: [],  # Human approval
            WorkflowPhase.PHASE_3_PLANS: ["dede", "dali", "gus"],  # Parallel
            WorkflowPhase.GATE_2_PLANS: [],  # Human approval
            WorkflowPhase.PHASE_4_TESTS: ["marie"],
            WorkflowPhase.GATE_3_TESTS: [],  # Human approval
            WorkflowPhase.PHASE_5_IMPLEMENTATION: ["dede", "dali", "gus"],  # Parallel TDD
            WorkflowPhase.PHASE_6_CREATE_PR: [],  # Program executes
            WorkflowPhase.PHASE_7_REVIEW: ["dede", "dali", "gus", "marie"],  # Parallel review
            WorkflowPhase.GATE_4_MERGE: [],  # Human approval
            WorkflowPhase.PHASE_8_CLEANUP: [],  # Program executes
        }
        return agent_map.get(self, [])
