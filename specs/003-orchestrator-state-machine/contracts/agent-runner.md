# Contract: AgentRunner Protocol

**Module**: `src/orchestrator/agent_runner.py`
**Type**: Python Protocol + Implementations

## Overview

The AgentRunner protocol defines the interface for executing AI agents. It enables pluggable agent execution across different providers (Claude, Gemini, Codex) and modes (CLI, SDK).

## Protocol Definition

```python
from typing import Protocol, Any

class AgentRunner(Protocol):
    """Protocol for AI agent execution.

    Implementations handle the specifics of invoking an AI agent,
    whether via CLI, SDK, or other mechanisms.
    """

    def dispatch(
        self,
        config: AgentConfig,
        context: dict[str, Any],
    ) -> AgentResult:
        """Execute an AI agent with the given configuration.

        Args:
            config: Complete agent configuration.
            context: Additional context (issue details, paths, etc.).

        Returns:
            AgentResult with execution outcome.

        Raises:
            AgentDispatchError: If agent fails to start.
            AgentExecutionError: If agent fails during execution.
            AgentTimeoutError: If execution exceeds timeout.
        """
        ...

    def is_available(self) -> bool:
        """Check if this runner is available on the system.

        Returns:
            True if the runner can be used, False otherwise.
        """
        ...

    def get_capabilities(self) -> list[str]:
        """List capabilities this runner supports.

        Returns:
            List of capability strings (e.g., ["skills", "plugins", "mcp"]).
        """
        ...
```

---

## AgentConfig Model

```python
class AgentConfig(BaseModel):
    """Configuration for dispatching an AI agent."""

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
    """Skills to bundle with the agent."""

    plugins: list[str] = Field(default_factory=list)
    """Plugins to include."""

    mcp_servers: list[str] = Field(default_factory=list)
    """MCP servers to configure."""

    timeout_seconds: int = Field(default=3600, gt=0)
    """Maximum execution time in seconds."""

    work_dir: Path | None = None
    """Working directory for agent execution."""

    class Config:
        frozen = True
```

**Validation Rules**:
- `provider` must be a valid AgentProvider enum value
- `model` must be non-empty
- `role` must be non-empty
- At least one of `prompt` or `skills` must be provided

---

## AgentResult Model

```python
class AgentResult(BaseModel):
    """Result from executing an AI agent."""

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

    class Config:
        frozen = True
```

---

## ClaudeCLIRunner Implementation

The primary implementation for this feature.

### Constructor

```python
class ClaudeCLIRunner:
    """Runs Claude agents via the Claude CLI."""

    def __init__(
        self,
        claude_path: str = "claude",
    ) -> None:
        """Initialize the Claude CLI runner.

        Args:
            claude_path: Path to claude executable (default: "claude").
        """
```

### dispatch

```python
def dispatch(
    self,
    config: AgentConfig,
    context: dict[str, Any],
) -> AgentResult:
    """Execute Claude CLI with the given configuration.

    Args:
        config: Agent configuration.
        context: Additional context dict with keys:
            - issue_number: int
            - issue_title: str
            - issue_body: str
            - worktree_path: Path
            - repo_path: Path

    Returns:
        AgentResult with execution outcome.

    Raises:
        AgentDispatchError: If claude CLI is not available.
        AgentExecutionError: If execution fails.
    """
```

**CLI Command Construction**:
```python
# Base command
cmd = [self.claude_path, "--model", config.model, "--print"]

# Add prompt
if config.prompt:
    cmd.extend(["-p", config.prompt])

# Add skills (if supported)
for skill in config.skills:
    cmd.extend(["--allowedTools", skill])

# Add plugins (if supported)
for plugin in config.plugins:
    cmd.extend(["--plugin", plugin])

# Add MCP servers (if supported)
for mcp in config.mcp_servers:
    cmd.extend(["--mcp", mcp])
```

### is_available

```python
def is_available(self) -> bool:
    """Check if Claude CLI is installed and accessible.

    Returns:
        True if `claude --version` succeeds.
    """
```

### get_capabilities

```python
def get_capabilities(self) -> list[str]:
    """List Claude CLI capabilities.

    Returns:
        ["skills", "plugins", "mcp", "model_selection"]
    """
```

---

## Future Implementations

### ClaudeSDKRunner (Future)

For cloud deployment using Anthropic SDK.

```python
class ClaudeSDKRunner:
    """Runs Claude agents via Anthropic SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize with API key (from env if not provided)."""
        ...
```

### GeminiCLIRunner (Future)

For Gemini AI support.

```python
class GeminiCLIRunner:
    """Runs Gemini agents via gcloud CLI."""
    ...
```

### CodexCLIRunner (Future)

For OpenAI Codex support.

```python
class CodexCLIRunner:
    """Runs Codex agents via OpenAI CLI."""
    ...
```

---

## Error Handling

```python
class AgentError(OrchestratorError):
    """Base exception for agent-related errors."""
    pass

class AgentDispatchError(AgentError):
    """Agent failed to start."""
    error_code = "AGENT_DISPATCH_ERROR"

class AgentExecutionError(AgentError):
    """Agent failed during execution."""
    error_code = "AGENT_EXECUTION_ERROR"

class AgentTimeoutError(AgentError):
    """Agent execution exceeded timeout."""
    error_code = "AGENT_TIMEOUT"

class AgentNotAvailableError(AgentError):
    """Agent runner is not available on this system."""
    error_code = "AGENT_NOT_AVAILABLE"
```

---

## Runner Selection

```python
def get_runner(config: AgentConfig) -> AgentRunner:
    """Get appropriate runner for the configuration.

    Args:
        config: Agent configuration.

    Returns:
        AgentRunner instance.

    Raises:
        AgentNotAvailableError: If no runner available for config.
    """
    if config.provider == AgentProvider.CLAUDE:
        if config.mode == ExecutionMode.CLI:
            runner = ClaudeCLIRunner()
            if not runner.is_available():
                raise AgentNotAvailableError(
                    "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
                )
            return runner
        else:
            raise AgentNotAvailableError(
                "Claude SDK mode not yet implemented"
            )
    else:
        raise AgentNotAvailableError(
            f"Provider {config.provider} not yet implemented"
        )
```

---

## Usage Example

```python
from orchestrator.agent_runner import ClaudeCLIRunner, get_runner
from orchestrator.models import AgentConfig, AgentProvider, ExecutionMode

# Direct usage
runner = ClaudeCLIRunner()
if runner.is_available():
    result = runner.dispatch(
        AgentConfig(
            provider=AgentProvider.CLAUDE,
            mode=ExecutionMode.CLI,
            model="sonnet",
            role="@duc",
            prompt="Design the authentication system",
        ),
        context={
            "issue_number": 123,
            "issue_title": "Add OAuth2",
            "worktree_path": Path("/path/to/worktree"),
        },
    )
    if result.success:
        print("Agent completed successfully")
    else:
        print(f"Agent failed: {result.error_message}")

# Via factory
config = AgentConfig(...)
runner = get_runner(config)
result = runner.dispatch(config, context)
```

---

## Testing Considerations

### Mocking the Protocol

```python
from unittest.mock import MagicMock

def create_mock_runner(success: bool = True) -> AgentRunner:
    """Create a mock AgentRunner for testing."""
    mock = MagicMock(spec=AgentRunner)
    mock.is_available.return_value = True
    mock.get_capabilities.return_value = ["skills", "plugins"]
    mock.dispatch.return_value = AgentResult(
        success=success,
        exit_code=0 if success else 1,
        stdout="Mock output",
        duration_seconds=1.0,
    )
    return mock
```

### Testing CLI Runner

```python
def test_claude_cli_dispatch(tmp_path):
    """Test ClaudeCLIRunner dispatches correctly."""
    runner = ClaudeCLIRunner()
    if not runner.is_available():
        pytest.skip("Claude CLI not installed")

    result = runner.dispatch(
        AgentConfig(
            provider=AgentProvider.CLAUDE,
            mode=ExecutionMode.CLI,
            model="haiku",
            role="test",
            prompt="echo 'test'",
        ),
        context={"worktree_path": tmp_path},
    )
    assert result.success or "error" in result.stderr.lower()
```
