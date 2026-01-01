"""Tests for git worktree manager."""

import pytest

from farmcode.git.worktree_manager import WorktreeManager


def test_slugify():
    """Test slug generation."""
    manager = WorktreeManager.__new__(WorktreeManager)

    assert manager._slugify("Add User Auth") == "add-user-auth"
    assert manager._slugify("Fix Bug #123") == "fix-bug-123"
    assert manager._slugify("Feature: Dark Mode!!!") == "feature-dark-mode"
    assert manager._slugify("Support UTF-8 Émojis 🚀") == "support-utf-8-mojis"


def test_create_worktree(mock_worktree_manager, mock_config):
    """Test creating a worktree."""
    manager = mock_worktree_manager

    # Create worktree
    info = manager.create_worktree(
        issue_number=123,
        title="Add User Authentication",
    )

    assert info.issue_number == 123
    assert info.branch_name == "123-add-user-authentication"
    assert info.worktree_path.exists()

    # Verify .plans structure
    plans_dir = info.worktree_path / ".plans" / "123"
    assert plans_dir.exists()
    assert (plans_dir / "specs").exists()
    assert (plans_dir / "plans").exists()
    assert (plans_dir / "reviews").exists()
    assert (plans_dir / "qa").exists()
    assert (plans_dir / "README.md").exists()

    # Verify README content
    readme_content = (plans_dir / "README.md").read_text()
    assert "Feature #123: Add User Authentication" in readme_content
    assert "specs/" in readme_content


def test_create_worktree_duplicate_branch(mock_worktree_manager):
    """Test that creating duplicate branch fails."""
    manager = mock_worktree_manager

    # Create first worktree
    manager.create_worktree(123, "Test Feature")

    # Try to create again
    with pytest.raises(ValueError, match="Branch .* already exists"):
        manager.create_worktree(123, "Test Feature")


def test_delete_worktree(mock_worktree_manager):
    """Test deleting a worktree."""
    manager = mock_worktree_manager

    # Create worktree
    info = manager.create_worktree(123, "Test Feature")

    # Delete
    manager.delete_worktree(info.branch_name)

    # Verify deleted
    assert not info.worktree_path.exists()
    assert not manager.worktree_exists(info.branch_name)


def test_delete_nonexistent_worktree(mock_worktree_manager):
    """Test deleting nonexistent worktree fails."""
    manager = mock_worktree_manager

    with pytest.raises(ValueError, match="does not exist"):
        manager.delete_worktree("nonexistent-branch")


def test_worktree_exists(mock_worktree_manager):
    """Test checking if worktree exists."""
    manager = mock_worktree_manager

    assert not manager.worktree_exists("123-test-feature")

    # Create worktree
    info = manager.create_worktree(123, "Test Feature")

    assert manager.worktree_exists(info.branch_name)
