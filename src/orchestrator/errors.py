"""Custom exceptions for the Orchestrator module.

All errors inherit from OrchestratorError and include an error_code
for consistent error handling and debugging.
"""


class OrchestratorError(Exception):
    """Base exception for all orchestrator errors.

    All orchestrator-specific exceptions inherit from this class
    to allow consistent error handling.

    Attributes:
        message: Human-readable error description.
        error_code: Machine-readable error code for programmatic handling.
    """

    error_code: str = "UNKNOWN_ERROR"

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Initialize OrchestratorError.

        Args:
            message: Human-readable error description.
            error_code: Optional error code override.
        """
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"[{self.error_code}] {self.message}"


# State Machine Errors


class WorkflowNotFoundError(OrchestratorError):
    """No workflow exists for the given issue number.

    Raised when attempting to access state for an issue
    that has no associated workflow.
    """

    error_code: str = "WORKFLOW_NOT_FOUND"


class WorkflowAlreadyExistsError(OrchestratorError):
    """Workflow already in progress for this issue.

    Raised when attempting to create a new workflow
    for an issue that already has an active workflow.
    """

    error_code: str = "WORKFLOW_EXISTS"


class InvalidStateTransition(OrchestratorError):
    """Requested state transition is not allowed.

    Raised when attempting a transition that violates
    the state machine rules (e.g., going backwards).
    """

    error_code: str = "INVALID_TRANSITION"


class InvalidStateError(OrchestratorError):
    """Operation not valid for current workflow state.

    Raised when an operation is attempted in a state
    where it is not allowed.
    """

    error_code: str = "INVALID_STATE"


class StateFileCorruptedError(OrchestratorError):
    """State file is malformed or unreadable.

    Raised when the persisted state file cannot be
    parsed or contains invalid data.
    """

    error_code: str = "STATE_CORRUPTED"


# Agent Errors


class AgentError(OrchestratorError):
    """Base exception for agent-related errors."""

    error_code: str = "AGENT_ERROR"


class AgentDispatchError(AgentError):
    """Agent failed to start.

    Raised when the agent process fails to launch,
    typically due to misconfiguration or missing dependencies.
    """

    error_code: str = "AGENT_DISPATCH_ERROR"


class AgentExecutionError(AgentError):
    """Agent failed during execution.

    Raised when the agent process starts but fails
    during execution with a non-zero exit code.
    """

    error_code: str = "AGENT_EXECUTION_ERROR"


class AgentTimeoutError(AgentError):
    """Agent execution exceeded timeout.

    Raised when the agent process does not complete
    within the configured timeout period.
    """

    error_code: str = "AGENT_TIMEOUT"


class AgentNotAvailableError(AgentError):
    """Agent runner is not available on this system.

    Raised when the required agent runner (e.g., Claude CLI)
    is not installed or accessible.
    """

    error_code: str = "AGENT_NOT_AVAILABLE"


# Phase Execution Errors


class Phase1Error(OrchestratorError):
    """Error during Phase 1 execution.

    Base class for Phase 1 specific errors including
    issue creation, branch creation, worktree setup, etc.
    """

    error_code: str = "PHASE_1_ERROR"


class IssueCreationError(Phase1Error):
    """Failed to create GitHub issue.

    Raised when the GitHub API call to create an issue fails.
    """

    error_code: str = "ISSUE_CREATION_ERROR"


class BranchCreationError(Phase1Error):
    """Failed to create branch.

    Raised when branch creation fails, often due to
    the branch already existing or permission issues.
    """

    error_code: str = "BRANCH_CREATION_ERROR"


class WorktreeCreationError(Phase1Error):
    """Failed to create git worktree.

    Raised when worktree creation fails, typically due to
    path conflicts or git configuration issues.
    """

    error_code: str = "WORKTREE_CREATION_ERROR"


class PlansInitializationError(Phase1Error):
    """Failed to initialize .plans directory structure.

    Raised when creating the .plans/{issue}/ directory
    structure fails.
    """

    error_code: str = "PLANS_INIT_ERROR"


# Polling Errors


class PollTimeoutError(OrchestratorError):
    """Polling timed out without detecting signal.

    Raised when the polling mechanism for agent completion
    or human approval exceeds the configured timeout.
    """

    error_code: str = "POLL_TIMEOUT"


class PollError(OrchestratorError):
    """Error during signal polling.

    Raised when an error occurs while polling for signals,
    such as GitHub API failures.
    """

    error_code: str = "POLL_ERROR"


# Label Sync Errors


class LabelSyncError(OrchestratorError):
    """Error during label synchronization.

    Raised when updating GitHub issue labels fails.
    """

    error_code: str = "LABEL_SYNC_ERROR"
