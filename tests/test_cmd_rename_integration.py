"""Integration tests for cmd_rename module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_rename import rename_command


def test_rename_command_with_names(gitspaces_project, monkeypatch, capsys):
    """Test renaming a space with both names provided."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.old_name = "feature"
    args.new_name = "renamed-feature"

    rename_command(args)

    # Verify space was renamed
    assert not project_data["feature_space"].exists()
    assert (project_data["project_path"] / "renamed-feature").exists()

    # Verify success message
    captured = capsys.readouterr()
    assert "Renamed space" in captured.out


def test_rename_command_not_in_project(temp_home, monkeypatch, capsys):
    """Test renaming when not in a project directory."""
    # Change to home directory
    monkeypatch.chdir(temp_home)

    args = Mock()
    args.old_name = "main"
    args.new_name = "renamed"

    rename_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "Not in a GitSpaces project" in captured.out


def test_rename_command_space_not_found(gitspaces_project, monkeypatch, capsys):
    """Test renaming non-existent space."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.old_name = "nonexistent"
    args.new_name = "renamed"

    rename_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_rename_command_target_exists(gitspaces_project, monkeypatch, capsys):
    """Test renaming to a name that already exists."""
    project_data = gitspaces_project

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.old_name = "feature"
    args.new_name = "main"  # Already exists

    rename_command(args)

    # Verify error message
    captured = capsys.readouterr()
    assert "already exists" in captured.out


def test_rename_sleeping_space(gitspaces_project, monkeypatch, capsys):
    """Test renaming a sleeping space."""
    project_data = gitspaces_project

    # Put a space to sleep
    import shutil

    sleeping_space = project_data["zzz_dir"] / "sleep1"
    shutil.copytree(project_data["feature_space"], sleeping_space)
    shutil.rmtree(project_data["feature_space"])

    # Change to project directory
    monkeypatch.chdir(project_data["main_space"])

    args = Mock()
    args.old_name = ".zzz/sleep1"
    args.new_name = "sleep2"

    rename_command(args)

    # Verify sleeping space was renamed
    assert not sleeping_space.exists()
    assert (project_data["zzz_dir"] / "sleep2").exists()
