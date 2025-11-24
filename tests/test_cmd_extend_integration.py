"""Integration tests for cmd_extend module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_extend import extend_command


def test_extend_command_with_defaults(gitspaces_project, monkeypatch, capsys):
    """Test extending with default settings."""
    project_data = gitspaces_project
    
    # Change to main space directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.num_spaces = 2
    args.space = None
    
    extend_command(args)
    
    # Verify new spaces were created in .zzz
    zzz_contents = list(project_data["zzz_dir"].iterdir())
    assert len(zzz_contents) >= 2
    
    # Verify success message
    captured = capsys.readouterr()
    assert "Successfully created" in captured.out


def test_extend_command_with_specific_space(gitspaces_project, monkeypatch, capsys):
    """Test extending from a specific space."""
    project_data = gitspaces_project
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.num_spaces = 1
    args.space = "feature"
    
    extend_command(args)
    
    # Verify new space was created
    zzz_contents = list(project_data["zzz_dir"].iterdir())
    assert len(zzz_contents) >= 1
    
    # Verify success message
    captured = capsys.readouterr()
    assert "Successfully created" in captured.out


def test_extend_command_not_in_project(temp_home, monkeypatch, capsys):
    """Test extending when not in a project directory."""
    # Change to home directory
    monkeypatch.chdir(temp_home)
    
    args = Mock()
    args.num_spaces = 1
    args.space = None
    
    extend_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "Not in a GitSpaces project" in captured.out


def test_extend_command_no_active_spaces(gitspaces_project, monkeypatch, capsys):
    """Test extending when no active spaces exist."""
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
    args.num_spaces = 1
    args.space = None
    
    extend_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "No active spaces available" in captured.out


def test_extend_command_space_not_found(gitspaces_project, monkeypatch, capsys):
    """Test extending from non-existent space."""
    project_data = gitspaces_project
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.num_spaces = 1
    args.space = "nonexistent"
    
    extend_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_extend_command_from_sleeping_space(gitspaces_project, monkeypatch, capsys):
    """Test that extending from a sleeping space is prevented."""
    project_data = gitspaces_project
    
    # Put a space to sleep
    import shutil
    sleeping_space = project_data["zzz_dir"] / "sleep1"
    shutil.copytree(project_data["feature_space"], sleeping_space)
    
    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.num_spaces = 1
    args.space = ".zzz/sleep1"
    
    extend_command(args)
    
    # Verify error message
    captured = capsys.readouterr()
    assert "not found or is sleeping" in captured.out


def test_extend_command_multiple_spaces(gitspaces_project, monkeypatch, capsys):
    """Test extending with multiple spaces."""
    project_data = gitspaces_project
    
    # Change to main space directory
    monkeypatch.chdir(project_data["main_space"])
    
    args = Mock()
    args.num_spaces = 3
    args.space = None
    
    extend_command(args)
    
    # Verify new spaces were created
    zzz_contents = list(project_data["zzz_dir"].iterdir())
    assert len(zzz_contents) >= 3
    
    # Verify success message
    captured = capsys.readouterr()
    assert "Successfully created 3" in captured.out
