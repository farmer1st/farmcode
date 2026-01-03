"""Pydantic models for the Orchestrator module.

This module defines all data models used by the orchestrator including:
- Enums for state, providers, modes, and signals
- State tracking models
- Agent configuration models
- Phase execution models
- Polling result models
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Enums
# =============================================================================


class WorkflowState(str, Enum):
    """Workflow states for the orchestrator state machine.

    The workflow progresses through these states linearly.
    Only forward transitions are allowed.
    """

    IDLE = "idle"
    """Initial state before workflow starts."""

    PHASE_1 = "phase_1"
    """Phase 1: Issue setup (create issue, branch, worktree, .plans)."""

    PHASE_2 = "phase_2"
    """Phase 2: Specification (agent dispatch, polling, approval)."""

    GATE_1 = "gate_1"
    """Gate 1: Awaiting human approval."""

    DONE = "done"
    """Terminal state: workflow complete."""


class AgentProvider(str, Enum):
    """Supported AI agent providers.

    Currently only CLAUDE is implemented; others are planned for future.
    """

    CLAUDE = "claude"
    """Anthropic Claude (implemented)."""

    GEMINI = "gemini"
    """Google Gemini (future)."""

    CODEX = "codex"
    """OpenAI Codex (future)."""


class ExecutionMode(str, Enum):
    """Agent execution modes.

    Determines how the agent is invoked.
    """

    CLI = "cli"
    """Command-line interface execution."""

    SDK = "sdk"
    """SDK/API call execution (future)."""


class SignalType(str, Enum):
    """Types of completion signals to poll for."""

    AGENT_COMPLETE = "agent_complete"
    """Agent posted completion signal (contains checkmark emoji)."""

    HUMAN_APPROVAL = "human_approval"
    """Human posted approval (contains 'approved' case-insensitive)."""


# =============================================================================
# State Models
# =============================================================================


class StateTransition(BaseModel):
    """Records a single state change event.

    Immutable record of a workflow state transition.
    """

    from_state: WorkflowState
    """State before the transition."""

    to_state: WorkflowState
    """State after the transition."""

    trigger: str
    """What caused the transition (e.g., 'phase_1_complete')."""

    timestamp: datetime
    """When the transition occurred (UTC)."""

    model_config = {"frozen": True}


class OrchestratorState(BaseModel):
    """Complete workflow state, persisted to .plans/{issue}/state.json.

    This model represents the full state of an orchestrator workflow
    for a specific GitHub issue.
    """

    issue_number: int = Field(gt=0)
    """GitHub issue number (primary key)."""

    current_state: WorkflowState = WorkflowState.IDLE
    """Current workflow state."""

    feature_name: str
    """Feature slug (e.g., 'add-auth', kebab-case)."""

    branch_name: str | None = None
    """Created branch name (set after Phase 1 branch step)."""

    worktree_path: Path | None = None
    """Worktree path (set after Phase 1 worktree step)."""

    phase1_steps: list[str] = Field(default_factory=list)
    """Completed Phase 1 steps: ['issue', 'branch', 'worktree', 'plans']."""

    phase2_agent_complete: bool = False
    """Agent posted completion signal (checkmark emoji)."""

    phase2_human_approved: bool = False
    """Human posted 'approved' comment."""

    history: list[StateTransition] = Field(default_factory=list)
    """Append-only transition history."""

    created_at: datetime
    """Workflow start time (UTC)."""

    updated_at: datetime
    """Last state change time (UTC)."""

    model_config = {"frozen": False}  # State is mutable


# =============================================================================
# Agent Configuration Models
# =============================================================================


class AgentConfig(BaseModel):
    """Configuration for dispatching an AI agent.

    Supports flexible agent configuration for different providers
    and execution modes.
    """

    provider: AgentProvider
    """AI provider (claude, gemini, codex)."""

    mode: ExecutionMode = ExecutionMode.CLI
    """Execution mode (cli or sdk)."""

    model: str
    """Model name (e.g., 'sonnet', 'opus', 'haiku')."""

    role: str
    """Agent role/persona (e.g., '@duc' for architect)."""

    prompt: str | None = None
    """Base prompt or instruction for the agent."""

    skills: list[str] = Field(default_factory=list)
    """Skills to bundle with the agent (e.g., ['/speckit.specify'])."""

    plugins: list[str] = Field(default_factory=list)
    """Plugins to include."""

    mcp_servers: list[str] = Field(default_factory=list)
    """MCP servers to configure."""

    timeout_seconds: int = Field(default=3600, gt=0)
    """Maximum execution time in seconds."""

    work_dir: Path | None = None
    """Working directory for agent execution."""

    model_config = {"frozen": True}


class AgentResult(BaseModel):
    """Result from executing an AI agent.

    Captures the outcome of agent execution including
    exit codes, output, and timing.
    """

    success: bool
    """Whether execution completed successfully."""

    exit_code: int | None = None
    """Process exit code (CLI mode only)."""

    stdout: str = ""
    """Captured standard output."""

    stderr: str = ""
    """Captured standard error."""

    duration_seconds: float | None = None
    """Execution duration in seconds."""

    error_message: str | None = None
    """Error details if execution failed."""

    model_config = {"frozen": True}


# =============================================================================
# Phase Execution Models
# =============================================================================


class Phase1Request(BaseModel):
    """Request to start Phase 1 execution.

    Contains the information needed to create a new feature workflow.
    """

    feature_description: str = Field(min_length=1)
    """Natural language feature description."""

    feature_name: str | None = None
    """Optional feature slug (derived from description if not provided)."""

    labels: list[str] = Field(default_factory=list)
    """Additional labels to apply to the GitHub issue."""

    model_config = {"frozen": True}


class Phase2Config(BaseModel):
    """Configuration for Phase 2 execution.

    Defines how the specification phase should run
    including agent configuration and polling settings.
    """

    agent_config: AgentConfig
    """Agent to dispatch for specification work."""

    poll_interval_seconds: int = Field(default=30, gt=0)
    """Seconds between polling attempts."""

    poll_timeout_seconds: int = Field(default=3600, gt=0)
    """Total timeout for polling (default 1 hour)."""

    model_config = {"frozen": True}


class PhaseResult(BaseModel):
    """Result from phase execution.

    Captures the outcome of executing a workflow phase.
    """

    success: bool
    """Whether phase completed successfully."""

    phase: str
    """Which phase ('phase_1' or 'phase_2')."""

    artifacts_created: list[str] = Field(default_factory=list)
    """List of created artifacts (e.g., 'issue#123', 'branch:123-auth')."""

    steps_completed: list[str] = Field(default_factory=list)
    """Completed step names."""

    error: str | None = None
    """Error message if phase failed."""

    duration_seconds: float | None = None
    """Execution duration in seconds."""

    model_config = {"frozen": True}


# =============================================================================
# Polling Models
# =============================================================================


class PollResult(BaseModel):
    """Result from polling for a signal.

    Captures whether a signal was detected and the
    details of the matching comment.
    """

    detected: bool
    """Whether the signal was found."""

    signal_type: SignalType
    """Type of signal that was polled for."""

    comment_id: int | None = None
    """ID of the matching comment."""

    comment_body: str | None = None
    """Body of the matching comment."""

    comment_author: str | None = None
    """Author of the matching comment."""

    poll_count: int = 0
    """Number of poll attempts made."""

    model_config = {"frozen": True}


# =============================================================================
# Operation Result
# =============================================================================


class OperationStatus(str, Enum):
    """Status of an orchestrator operation."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class OperationResult(BaseModel):
    """Generic result for orchestrator operations.

    Used for operations like label sync that don't return
    phase-specific results.
    """

    status: OperationStatus
    """Operation status."""

    message: str | None = None
    """Optional status message."""

    details: dict[str, Any] = Field(default_factory=dict)
    """Additional details about the operation."""

    model_config = {"frozen": True}
