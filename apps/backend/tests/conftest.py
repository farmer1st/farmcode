"""Pytest configuration and fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from farmcode.adapters.github_adapter import GitHubAdapter
from farmcode.config import FarmCodeSettings, reset_settings
from farmcode.git.worktree_manager import WorktreeManager
from farmcode.orchestrator import Orchestrator
from farmcode.storage.state_store import StateStore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir, monkeypatch):
    """Create a mock configuration for testing."""
    config_data = {
        "repository": {
            "main": "test-org/test-repo",
            "gitops": "test-org/test-gitops",
            "ai_agents": "test-org/test-agents",
        },
        "paths": {
            "worktree_base": str(temp_dir / "worktrees"),
            "keys_dir": str(temp_dir / "keys"),
            "gh_agent_script": str(temp_dir / "gh-agent"),
        },
        "orchestrator": {
            "poll_interval": 1,
            "max_parallel_agents": 2,
        },
        "claude": {
            "model": "claude-sonnet-4-20250514",
        },
    }

    # Create directories
    (temp_dir / "worktrees").mkdir()
    (temp_dir / "keys").mkdir()

    # Create dummy gh-agent script
    gh_agent_script = temp_dir / "gh-agent"
    gh_agent_script.write_text("#!/bin/bash\necho 'mock gh-agent'")
    gh_agent_script.chmod(0o755)

    # Create dummy key files
    for agent in ["duc", "baron", "dede"]:
        (temp_dir / "keys" / f"{agent}.pem").write_text("mock-key")

    # Create settings
    settings = FarmCodeSettings(**config_data)

    # Mock get_settings to return our test settings
    def mock_get_settings(*args, **kwargs):
        return settings

    monkeypatch.setattr("farmcode.config.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.adapters.github_adapter.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.git.worktree_manager.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.mcp.server.get_settings", mock_get_settings)

    # Create agents config
    settings._agents = {
        "duc": MagicMock(
            app_id="123",
            install_id="456",
            handle="duc",
            name="Viollet-le-Duc",
            model="sonnet",
        ),
        "baron": MagicMock(
            app_id="789",
            install_id="012",
            handle="baron",
            name="Baron Haussmann",
            model="sonnet",
        ),
    }

    yield settings

    # Reset settings after test
    reset_settings()


@pytest.fixture
def state_store(temp_dir):
    """Create a state store for testing."""
    return StateStore(storage_dir=temp_dir / "farmcode")


@pytest.fixture
def mock_github_adapter(monkeypatch):
    """Create a mock GitHub adapter."""
    mock = MagicMock(spec=GitHubAdapter)

    # Mock methods
    mock.create_issue.return_value = MagicMock(
        issue_id="123",
        title="Test Issue",
        body="Test body",
        labels=["farmcode"],
        comments=[],
    )

    mock.post_comment.return_value = "https://github.com/test/test/issues/123#comment-1"

    mock.get_issue_context.return_value = MagicMock(
        issue_id="123",
        title="Test Issue",
        body="Test body",
        labels=["farmcode"],
        comments=[],
    )

    return mock


@pytest.fixture
def mock_worktree_manager(temp_dir, monkeypatch):
    """Create a mock worktree manager."""
    from git import Repo

    # Create a mock git repo
    main_repo_path = temp_dir / "test-repo"
    main_repo_path.mkdir()

    # Initialize git repo
    repo = Repo.init(str(main_repo_path))

    # Create initial commit
    readme = main_repo_path / "README.md"
    readme.write_text("# Test Repo")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Create main branch
    repo.head.reference = repo.heads.main = repo.create_head("main")

    # Create worktree manager
    manager = WorktreeManager(main_repo_path=main_repo_path)

    # Mock git operations to avoid actual GitHub pushes
    def mock_push(*args, **kwargs):
        pass

    monkeypatch.setattr("git.remote.Remote.push", mock_push)

    return manager


@pytest.fixture
def orchestrator(mock_config, state_store, mock_github_adapter, mock_worktree_manager):
    """Create an orchestrator for testing."""
    from farmcode.orchestrator.phase_manager import PhaseManager

    # Create phase manager with mocked dependencies
    phase_manager = PhaseManager(
        worktree_manager=mock_worktree_manager,
        github_adapter=mock_github_adapter,
    )

    # Create orchestrator
    orch = Orchestrator(
        phase_manager=phase_manager,
        state_store=state_store,
        poll_interval=1,
    )

    return orch
