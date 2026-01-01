"""Agent dispatcher for spawning Claude CLI agents with MCP."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from farmcode.config import get_settings
from farmcode.models.phase import WorkflowPhase


class AgentSession(BaseModel):
    """Information about a running agent session."""

    agent_handle: str
    issue_number: int
    phase: WorkflowPhase
    process_id: int
    worktree_path: Path


class AgentDispatcher:
    """Dispatches Claude CLI agents with MCP configuration."""

    def __init__(self, mcp_server_url: str = "http://127.0.0.1:8000"):
        """Initialize agent dispatcher.

        Args:
            mcp_server_url: URL of the running MCP server
        """
        self.mcp_server_url = mcp_server_url
        self.settings = get_settings()
        self.active_sessions: dict[str, AgentSession] = {}

    def _build_agent_prompt(
        self,
        agent_handle: str,
        issue_number: int,
        phase: WorkflowPhase,
    ) -> str:
        """Build the initial prompt for the agent.

        Args:
            agent_handle: Agent handle (e.g., "duc")
            issue_number: GitHub issue number
            phase: Current workflow phase

        Returns:
            Prompt text
        """
        # Get agent config
        agent_config = self.settings.get_agent_config(agent_handle)

        prompts = {
            WorkflowPhase.PHASE_2_SPECS: f"""You are {agent_config.name} (@{agent_handle}), the architecture specialist.

Your task: Review issue #{issue_number} and write architecture specifications.

**Instructions**:
1. Use `task_get_context` to read the issue details
2. Design the system architecture for this feature
3. Write specs to `.plans/{issue_number}/specs/` directory
4. Use `task_signal_complete` when done with a summary

**Available MCP Tools**:
- task_get_context(issue_number) - Get issue details and context
- task_post_comment(issue_number, comment) - Post updates
- task_signal_complete(issue_number, summary, artifacts) - Mark complete

Begin by getting the issue context.
""",
        }

        return prompts.get(
            phase,
            f"Work on issue #{issue_number} for {phase.value}",
        )

    def dispatch(
        self,
        agent_handle: str,
        issue_number: int,
        worktree_path: Path,
        phase: WorkflowPhase,
    ) -> subprocess.Popen:
        """Spawn a Claude CLI agent with MCP configuration.

        Args:
            agent_handle: Agent handle (e.g., "duc")
            issue_number: GitHub issue number
            worktree_path: Path to git worktree
            phase: Current workflow phase

        Returns:
            Running subprocess

        Raises:
            ValueError: If agent already dispatched for this issue
        """
        # Check if already running
        session_key = f"{agent_handle}_{issue_number}"
        if session_key in self.active_sessions:
            msg = f"Agent {agent_handle} already dispatched for issue #{issue_number}"
            raise ValueError(msg)

        # Get agent configuration
        agent_config = self.settings.get_agent_config(agent_handle)

        # Build prompt
        prompt = self._build_agent_prompt(agent_handle, issue_number, phase)

        # Build Claude CLI command
        cmd = [
            "claude",
            "--model",
            agent_config.model,
            "--prompt",
            prompt,
        ]

        # Build environment with MCP configuration
        env = {
            **subprocess.os.environ.copy(),
            "FARMCODE_AGENT_HANDLE": agent_handle,
            "FARMCODE_MCP_SERVER_URL": self.mcp_server_url,
            "FARMCODE_ISSUE_NUMBER": str(issue_number),
        }

        # Spawn process in worktree directory
        process = subprocess.Popen(
            cmd,
            cwd=str(worktree_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Track session
        self.active_sessions[session_key] = AgentSession(
            agent_handle=agent_handle,
            issue_number=issue_number,
            phase=phase,
            process_id=process.pid,
            worktree_path=worktree_path,
        )

        return process

    def get_session(self, agent_handle: str, issue_number: int) -> AgentSession | None:
        """Get active session for an agent and issue.

        Args:
            agent_handle: Agent handle
            issue_number: GitHub issue number

        Returns:
            AgentSession if active, None otherwise
        """
        session_key = f"{agent_handle}_{issue_number}"
        return self.active_sessions.get(session_key)

    def remove_session(self, agent_handle: str, issue_number: int) -> None:
        """Remove session from tracking.

        Args:
            agent_handle: Agent handle
            issue_number: GitHub issue number
        """
        session_key = f"{agent_handle}_{issue_number}"
        self.active_sessions.pop(session_key, None)

    def get_all_sessions(self) -> list[AgentSession]:
        """Get all active agent sessions.

        Returns:
            List of active sessions
        """
        return list(self.active_sessions.values())
