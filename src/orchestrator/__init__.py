"""Orchestrator module for SDLC workflow state machine.

This module provides state machine orchestration for Phases 1-2 of the SDLC workflow.
It manages workflow state transitions, executes phase steps, dispatches AI agents,
and synchronizes GitHub labels with workflow state.

Public API:
    - OrchestratorService: Main facade for orchestration operations
    - Models: WorkflowState, OrchestratorState, AgentConfig, AgentResult, etc.
    - Errors: OrchestratorError and subclasses
    - AgentRunner: Protocol for pluggable agent execution
"""

# Version
__version__ = "0.1.0"

# Errors
# Runners
from orchestrator.agent_runner import AgentRunner, ClaudeCLIRunner, get_runner
from orchestrator.errors import (
    AgentDispatchError,
    AgentError,
    AgentExecutionError,
    AgentNotAvailableError,
    AgentTimeoutError,
    BranchCreationError,
    InvalidStateError,
    InvalidStateTransition,
    IssueCreationError,
    LabelSyncError,
    OrchestratorError,
    Phase1Error,
    PlansInitializationError,
    PollError,
    PollTimeoutError,
    StateFileCorruptedError,
    WorkflowAlreadyExistsError,
    WorkflowNotFoundError,
    WorktreeCreationError,
)

# Models
from orchestrator.models import (
    AgentConfig,
    AgentProvider,
    AgentResult,
    ExecutionMode,
    OperationResult,
    OperationStatus,
    OrchestratorState,
    Phase1Request,
    Phase2Config,
    PhaseResult,
    PollResult,
    SignalType,
    StateTransition,
    WorkflowState,
)

# Services
from orchestrator.service import OrchestratorService

__all__ = [
    # Version
    "__version__",
    # Services
    "OrchestratorService",
    # Agent Runners
    "AgentRunner",
    "ClaudeCLIRunner",
    "get_runner",
    # Enums
    "WorkflowState",
    "AgentProvider",
    "ExecutionMode",
    "SignalType",
    "OperationStatus",
    # State Models
    "StateTransition",
    "OrchestratorState",
    # Agent Models
    "AgentConfig",
    "AgentResult",
    # Phase Models
    "Phase1Request",
    "Phase2Config",
    "PhaseResult",
    # Polling Models
    "PollResult",
    # Operation Models
    "OperationResult",
    # Errors
    "OrchestratorError",
    "WorkflowNotFoundError",
    "WorkflowAlreadyExistsError",
    "InvalidStateTransition",
    "InvalidStateError",
    "StateFileCorruptedError",
    "AgentError",
    "AgentDispatchError",
    "AgentExecutionError",
    "AgentTimeoutError",
    "AgentNotAvailableError",
    "Phase1Error",
    "IssueCreationError",
    "BranchCreationError",
    "WorktreeCreationError",
    "PlansInitializationError",
    "PollTimeoutError",
    "PollError",
    "LabelSyncError",
]
