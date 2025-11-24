"""Integration tests for cmd_switch module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_switch import switch_command


def test_switch_command_with_space_name(gitspaces_project, monkeypatch):
    """Test switching to a space by name."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.space = "feature"

    # Mock chdir to track the call
    original_chdir = Path.cwd
    chdir_called_with = []

    def mock_chdir(path):
        chdir_called_with.append(path)

    from gitspaces.modules import runshell

    monkeypatch.setattr(runshell.fs, "chdir", mock_chdir)

    switch_command(args)

    # Verify chdir was called with feature space path
    assert len(chdir_called_with) == 1
    assert "feature" in str(chdir_called_with[0])


def test_switch_command_interactive_select(gitspaces_project, monkeypatch, mock_console_select):
    """Test switching with interactive selection."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    # Mock console select to return "feature"
    mock_console_select(["feature"])

    args = Mock()
    args.space = None

    # Mock chdir
    chdir_called_with = []

    def mock_chdir(path):
        chdir_called_with.append(path)

    from gitspaces.modules import runshell

    monkeypatch.setattr(runshell.fs, "chdir", mock_chdir)

    switch_command(args)

    # Verify chdir was called
    assert len(chdir_called_with) == 1
    assert "feature" in str(chdir_called_with[0])


def test_switch_command_not_in_project(temp_home, monkeypatch, capsys):
    """Test switching when not in a project directory."""
    # Change to home directory (not a project)
    monkeypatch.chdir(temp_home)

    args = Mock()
    args.space = "main"

    switch_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "Not in a GitSpaces project" in captured.out


def test_switch_command_space_not_found(gitspaces_project, monkeypatch, capsys):
    """Test switching to non-existent space."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.space = "nonexistent"

    switch_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_switch_command_no_spaces(gitspaces_project, monkeypatch, capsys):
    """Test switching when project has no spaces."""
    project_data = gitspaces_project

    # Remove all spaces
    import shutil

    shutil.rmtree(project_data["main_space"])
    shutil.rmtree(project_data["feature_space"])

    # Change to project directory
    monkeypatch.chdir(project_data["project_path"])

    args = Mock()
    args.space = None

    switch_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "No spaces found" in captured.out


def test_switch_command_sleeping_space(gitspaces_project, monkeypatch, capsys):
    """Test that switching to a sleeping space shows not found."""
    project_data = gitspaces_project

    # Create a sleeping space
    import shutil

    sleeping_space = project_data["zzz_dir"] / "sleep1"
    shutil.copytree(project_data["main_space"], sleeping_space)

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.space = ".zzz/sleep1"

    switch_command(args)

    # Verify error message (sleeping spaces are listed differently)
    captured = capsys.readouterr()
    assert "not found" in captured.out or "Cannot switch" in captured.out
