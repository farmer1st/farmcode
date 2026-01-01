"""MCP server for Farm Code agent tools."""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from farmcode.adapters.github_adapter import GitHubAdapter
from farmcode.config import get_settings
from farmcode.storage.state_store import StateStore


def create_mcp_server() -> FastMCP:
    """Create and configure the Farm Code MCP server.

    Returns:
        Configured FastMCP server instance
    """
    # Get agent handle from environment
    agent_handle = os.environ.get("FARMCODE_AGENT_HANDLE", "unknown")

    # Initialize dependencies
    settings = get_settings()
    state_store = StateStore()
    github_adapter = GitHubAdapter(
        repo=settings.repository.main,
        agent_handle=agent_handle,
    )

    # Create MCP server
    mcp = FastMCP("farmcode")

    @mcp.tool()
    async def task_get_context(issue_number: int) -> dict[str, Any]:
        """Get full context for a task/feature.

        Retrieves issue details, specifications, plans, and recent comments.

        Args:
            issue_number: GitHub issue number

        Returns:
            Dictionary containing:
            - issue: Issue details (title, body, labels)
            - state: Current workflow state
            - specs: Path to specs directory
            - plans: Path to plans directory
            - comments: Recent comments from other agents
        """
        # Get issue context from GitHub
        issue_context = github_adapter.get_issue_context(str(issue_number))

        # Get feature state
        feature_state = state_store.load(issue_number)

        # Build response
        context = {
            "issue": {
                "number": issue_number,
                "title": issue_context.title,
                "body": issue_context.body,
                "labels": issue_context.labels,
            },
            "state": feature_state.model_dump() if feature_state else None,
            "specs": f".plans/{issue_number}/specs/",
            "plans": f".plans/{issue_number}/plans/",
            "comments": [
                {
                    "author": comment.author,
                    "body": comment.body,
                    "created_at": comment.created_at.isoformat(),
                }
                for comment in issue_context.comments
            ],
        }

        return context

    @mcp.tool()
    async def task_post_comment(issue_number: int, comment: str) -> str:
        """Post a comment to the GitHub issue as this agent.

        Use this to:
        - Ask questions to the team
        - Share progress updates
        - Request clarification
        - Document decisions

        Args:
            issue_number: GitHub issue number
            comment: Comment body (supports GitHub markdown)

        Returns:
            Success message with comment URL
        """
        comment_url = github_adapter.post_comment(
            issue_id=str(issue_number),
            body=comment,
        )

        return f"Comment posted successfully: {comment_url}"

    @mcp.tool()
    async def task_signal_complete(
        issue_number: int,
        summary: str,
        artifacts: list[str] | None = None,
    ) -> str:
        """Signal that your task is complete.

        This marks your work as done in the current phase and posts a completion
        comment with ✅ marker.

        Args:
            issue_number: GitHub issue number
            summary: Brief summary of what was accomplished
            artifacts: Optional list of file paths created/modified

        Returns:
            Success message
        """
        # Build completion comment
        artifacts_text = ""
        if artifacts:
            artifacts_text = "\n\n**Artifacts:**\n" + "\n".join(f"- `{path}`" for path in artifacts)

        comment_body = f"""✅ **Task Complete** (@{agent_handle})

{summary}{artifacts_text}

Ready for next phase.
"""

        # Post completion comment
        github_adapter.post_comment(
            issue_id=str(issue_number),
            body=comment_body,
        )

        return f"Task marked complete for issue #{issue_number}"

    return mcp


def run_mcp_server() -> None:
    """Run the MCP server (for standalone mode).

    This is used when the MCP server runs as a separate process.
    For embedded mode, use create_mcp_server() instead.
    """
    mcp = create_mcp_server()

    # Get server configuration
    host = os.environ.get("FARMCODE_MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FARMCODE_MCP_PORT", "8000"))

    # Run server
    import uvicorn

    uvicorn.run(mcp.get_asgi_app(), host=host, port=port)


if __name__ == "__main__":
    run_mcp_server()
