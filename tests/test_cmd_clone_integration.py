"""Integration tests for cmd_clone module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_clone import clone_command
from gitspaces.modules.project import Project


def test_clone_command_with_directory(temp_git_repo, gitspaces_config, monkeypatch):
    """Test cloning a repository to a specific directory."""
    target_dir = gitspaces_config["projects_dir"] / "cloned-project"

    args = Mock()
    args.url = str(temp_git_repo)
    args.num_spaces = 2
    args.directory = str(target_dir.parent)

    # Change to temp directory
    monkeypatch.chdir(gitspaces_config["projects_dir"])

    clone_command(args)

    # Verify project was created
    project_path = target_dir.parent / temp_git_repo.name
    assert project_path.exists()
    assert (project_path / Project.DOTFILE).exists()


def test_clone_command_uses_config_path(temp_git_repo, gitspaces_config, monkeypatch):
    """Test cloning uses configured project path when no directory specified."""
    args = Mock()
    args.url = str(temp_git_repo)
    args.num_spaces = 1
    args.directory = None

    # Change to temp directory
    monkeypatch.chdir(gitspaces_config["projects_dir"])

    clone_command(args)

    # Verify project was created in config path
    project_path = gitspaces_config["projects_dir"] / temp_git_repo.name
    assert project_path.exists()
    assert (project_path / Project.DOTFILE).exists()


def test_clone_command_multiple_spaces(temp_git_repo, gitspaces_config, monkeypatch):
    """Test cloning with multiple spaces."""
    args = Mock()
    args.url = str(temp_git_repo)
    args.num_spaces = 3
    args.directory = None

    # Change to temp directory
    monkeypatch.chdir(gitspaces_config["projects_dir"])

    clone_command(args)

    # Verify project with spaces was created
    project_path = gitspaces_config["projects_dir"] / temp_git_repo.name
    assert project_path.exists()

    # Check that .zzz directory exists (for sleeping spaces)
    zzz_dir = project_path / ".zzz"
    assert zzz_dir.exists()


def test_clone_command_invalid_url(gitspaces_config, monkeypatch):
    """Test cloning with invalid URL raises error."""
    args = Mock()
    args.url = "https://invalid-url-that-does-not-exist.com/repo.git"
    args.num_spaces = 1
    args.directory = None

    # Change to temp directory
    monkeypatch.chdir(gitspaces_config["projects_dir"])

    with pytest.raises(Exception):
        clone_command(args)
