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


@pytest.fixture(autouse=True)
def mock_config(temp_dir, monkeypatch):
    """Create a mock configuration for testing.

    Auto-applied to all tests to ensure consistent mock environment.
    """
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
    for agent in ["duc", "baron", "dede", "orchestrator"]:
        (temp_dir / "keys" / f"{agent}.pem").write_text("mock-key")

    # Create agents.yaml file
    agents_yaml = temp_dir / "agents.yaml"
    agents_yaml.write_text("""agents:
  duc:
    name: "Viollet-le-Duc"
    app_id: "123"
    install_id: "456"
    model: "sonnet"
  baron:
    name: "Baron Haussmann"
    app_id: "789"
    install_id: "012"
    model: "sonnet"
  dede:
    name: "André Déde"
    app_id: "111"
    install_id: "222"
    model: "sonnet"
  orchestrator:
    name: "Orchestrator"
    app_id: "999"
    install_id: "888"
    model: "sonnet"
""")

    # Create settings
    settings = FarmCodeSettings(**config_data)

    # Set the agents config path to our temp agents.yaml
    settings._agents_path = agents_yaml

    # Mock get_settings to return our test settings
    def mock_get_settings(*args, **kwargs):
        return settings

    monkeypatch.setattr("farmcode.config.get_settings", mock_get_settings)
    # Note: github_adapter doesn't import get_settings, so we don't mock it there
    monkeypatch.setattr("farmcode.git.worktree_manager.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.mcp.server.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.orchestrator.github_poller.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.orchestrator.phase_manager.get_settings", mock_get_settings)
    monkeypatch.setattr("farmcode.orchestrator.agent_dispatcher.get_settings", mock_get_settings)

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

    # Track issue counter for sequential issue numbers
    issue_counter = [122]  # Use list to allow mutation in closure

    def create_issue_side_effect(title, body, labels):
        issue_counter[0] += 1
        return MagicMock(
            issue_number=issue_counter[0],
            title=title,
            body=body,
            labels=labels,
            comments=[],
        )

    # Mock methods
    mock.create_issue.side_effect = create_issue_side_effect

    mock.post_comment.return_value = "https://github.com/test/test/issues/123#comment-1"

    mock.get_issue_context.return_value = MagicMock(
        issue_number=123,
        title="Test Issue",
        body="Test body",
        labels=["farmcode"],
        comments=[],
    )

    return mock


@pytest.fixture
def mock_worktree_manager(temp_dir, mock_config, monkeypatch):
    """Create a mock worktree manager.

    Depends on mock_config to ensure settings are mocked before creating manager.
    """
    from git import Repo

    # Create a mock git repo in temp directory
    main_repo_path = temp_dir / "test-repo"
    main_repo_path.mkdir()

    # Initialize git repo
    repo = Repo.init(str(main_repo_path))

    # Create initial commit
    readme = main_repo_path / "README.md"
    readme.write_text("# Test Repo")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Create main branch - create the head first, then reference it
    if "main" not in [h.name for h in repo.heads]:
        main_branch = repo.create_head("main")
    else:
        main_branch = repo.heads["main"]
    repo.head.reference = main_branch

    # Create a mock remote 'origin'
    if "origin" not in [remote.name for remote in repo.remotes]:
        repo.create_remote("origin", url="https://github.com/test-org/test-repo.git")

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
    from farmcode.orchestrator.agent_dispatcher import AgentDispatcher
    from farmcode.orchestrator.github_poller import GitHubPoller
    from farmcode.orchestrator.phase_manager import PhaseManager

    # Create phase manager with mocked dependencies
    phase_manager = PhaseManager(
        worktree_manager=mock_worktree_manager,
        github_adapter=mock_github_adapter,
    )

    # Create mock github poller with mock adapter
    github_poller = GitHubPoller(github_adapter=mock_github_adapter)

    # Create mock agent dispatcher
    agent_dispatcher = MagicMock(spec=AgentDispatcher)

    # Create orchestrator with all mocked dependencies
    orch = Orchestrator(
        phase_manager=phase_manager,
        agent_dispatcher=agent_dispatcher,
        github_poller=github_poller,
        state_store=state_store,
        poll_interval=1,
    )

    return orch
