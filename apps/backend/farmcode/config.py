"""Configuration management for Farm Code."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for a single agent's GitHub App credentials."""

    app_id: Annotated[str, Field(description="GitHub App ID")]
    install_id: Annotated[str, Field(description="GitHub App Installation ID")]
    handle: Annotated[str, Field(description="Agent handle (e.g., 'duc', 'dede')")]
    name: Annotated[str, Field(description="Agent display name")]
    model: Annotated[str, Field(default="sonnet", description="Claude model to use")]


class RepositoryConfig(BaseModel):
    """Repository configuration."""

    main: Annotated[str, Field(description="Main repository (e.g., 'farmer1st/platform')")]
    gitops: Annotated[str | None, Field(default=None, description="GitOps repository")]
    ai_agents: Annotated[str, Field(description="AI agents repository")]


class PathsConfig(BaseModel):
    """Paths configuration."""

    worktree_base: Annotated[Path, Field(description="Base path for worktrees")]
    keys_dir: Annotated[Path, Field(description="Directory containing .pem files")]
    gh_agent_script: Annotated[Path, Field(description="Path to gh-agent script")]

    def __init__(self, **data):
        """Expand ~ in paths."""
        for key in ["worktree_base", "keys_dir", "gh_agent_script"]:
            if key in data and isinstance(data[key], str):
                data[key] = Path(data[key]).expanduser()
        super().__init__(**data)


class OrchestratorConfig(BaseModel):
    """Orchestrator settings."""

    poll_interval: Annotated[int, Field(default=10, description="Comment polling interval")]
    max_parallel_agents: Annotated[int, Field(default=4, description="Max parallel agents")]


class ClaudeConfig(BaseModel):
    """Claude configuration."""

    model: Annotated[str, Field(default="claude-sonnet-4-20250514", description="Claude model")]


class FarmCodeSettings(BaseModel):
    """Global Farm Code configuration loaded from YAML files."""

    repository: RepositoryConfig
    paths: PathsConfig
    orchestrator: OrchestratorConfig
    claude: ClaudeConfig

    # Cached agent configs
    _agents: dict[str, AgentConfig] | None = None

    @classmethod
    def load_from_yaml(
        cls,
        config_path: Path | None = None,
        agents_path: Path | None = None,
    ) -> FarmCodeSettings:
        """Load configuration from YAML files.

        Args:
            config_path: Path to farmcode.yaml (defaults to config/farmcode.yaml)
            agents_path: Path to agents.yaml (defaults to config/agents.yaml)
        """
        # Default paths relative to this file
        config_dir = Path(__file__).parent.parent / "config"

        if config_path is None:
            config_path = config_dir / "farmcode.yaml"

        if agents_path is None:
            agents_path = config_dir / "agents.yaml"

        # Load main config
        if not config_path.exists():
            msg = f"Config file not found: {config_path}"
            raise FileNotFoundError(msg)

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        settings = cls(**config_data)

        # Store agents path for lazy loading
        settings._agents_path = agents_path

        return settings

    def _load_agents_config(self) -> dict[str, AgentConfig]:
        """Load agent configurations from agents.yaml."""
        agents_path = getattr(self, "_agents_path", None)
        if agents_path is None:
            agents_path = Path(__file__).parent.parent / "config" / "agents.yaml"

        if not agents_path.exists():
            msg = f"Agents config not found: {agents_path}"
            raise FileNotFoundError(msg)

        with open(agents_path) as f:
            data = yaml.safe_load(f)

        agents = {}
        for handle, config in data.get("agents", {}).items():
            # Verify key file exists
            key_file = self.paths.keys_dir / f"{handle}.pem"
            if not key_file.exists():
                msg = f"Agent key not found: {key_file}"
                raise FileNotFoundError(msg)

            agents[handle] = AgentConfig(
                app_id=config["app_id"],
                install_id=config["install_id"],
                handle=handle,
                name=config["name"],
                model=config.get("model", self.claude.model),
            )

        return agents

    def get_agent_config(self, handle: str) -> AgentConfig:
        """Get configuration for a specific agent by handle."""
        if self._agents is None:
            self._agents = self._load_agents_config()

        handle_lower = handle.lower()
        if handle_lower not in self._agents:
            msg = f"Agent '{handle}' not configured in agents.yaml"
            raise ValueError(msg)

        return self._agents[handle_lower]

    def get_all_agent_handles(self) -> list[str]:
        """Get list of all configured agent handles."""
        if self._agents is None:
            self._agents = self._load_agents_config()

        return list(self._agents.keys())


# Global settings instance
_settings: FarmCodeSettings | None = None


def get_settings(
    config_path: Path | None = None,
    agents_path: Path | None = None,
) -> FarmCodeSettings:
    """Get the global settings instance (singleton).

    Args:
        config_path: Path to farmcode.yaml (only used on first call)
        agents_path: Path to agents.yaml (only used on first call)
    """
    global _settings
    if _settings is None:
        _settings = FarmCodeSettings.load_from_yaml(config_path, agents_path)
    return _settings


def reset_settings() -> None:
    """Reset the global settings (useful for testing)."""
    global _settings
    _settings = None
