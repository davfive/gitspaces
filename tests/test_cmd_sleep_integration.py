"""Integration tests for cmd_sleep module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_sleep import sleep_command
from gitspaces.modules.project import Project


def test_sleep_command_with_space_name(gitspaces_project, monkeypatch, capsys):
    """Test putting a space to sleep by name."""
    project_data = gitspaces_project
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.space = "feature"
    
    sleep_command(args)
    
    # Verify feature space was moved to .zzz
    assert not project_data["feature_space"].exists()
    zzz_contents = list(project_data["zzz_dir"].iterdir())
    assert len(zzz_contents) > 0


def test_sleep_command_interactive_select(gitspaces_project, monkeypatch, mock_console_select, capsys):
    """Test sleeping with interactive selection."""
    project_data = gitspaces_project
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    # Mock console select to return "feature"
    mock_console_select(["feature"])
    
    args = Mock()
    args.space = None
    
    sleep_command(args)
    
    # Verify feature space was moved
    assert not project_data["feature_space"].exists()


def test_sleep_command_not_in_project(temp_home, monkeypatch, capsys):
    """Test sleeping when not in a project directory."""
    # Change to home directory
    monkeypatch.chdir(temp_home)
    
    args = Mock()
    args.space = "main"
    
    sleep_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "Not in a GitSpaces project" in captured.out


def test_sleep_command_no_active_spaces(gitspaces_project, monkeypatch, capsys):
    """Test sleeping when no active spaces exist."""
    project_data = gitspaces_project
    
    # Move all spaces to .zzz
    import shutil
    for space in ["main", "feature"]:
        src = project_data["project_path"] / space
        if src.exists():
            shutil.move(str(src), str(project_data["zzz_dir"] / space))
    
    # Change to project directory
    monkeypatch.chdir(project_data["project_path"])
    
    args = Mock()
    args.space = None
    
    sleep_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "No active spaces" in captured.out


def test_sleep_command_with_wake_prompt(gitspaces_project, monkeypatch, mock_console_confirm, mock_console_select, mock_console_input, capsys):
    """Test sleeping with wake prompt interaction."""
    project_data = gitspaces_project
    
    # First put a space to sleep to have a sleeping space available
    import shutil
    sleeping_space = project_data["zzz_dir"] / "sleep1"
    shutil.copytree(project_data["main_space"], sleeping_space)
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    # Mock console interactions
    mock_console_confirm([True])  # Confirm wake another
    mock_console_select([".zzz/sleep1"])  # Select sleeping space
    mock_console_input(["awakened"])  # New name for woken space
    
    args = Mock()
    args.space = "feature"
    
    sleep_command(args)
    
    # Verify feature space was moved to .zzz
    assert not project_data["feature_space"].exists()
    
    # Verify sleeping space was woken with new name
    assert not sleeping_space.exists()
    assert (project_data["project_path"] / "awakened").exists()
