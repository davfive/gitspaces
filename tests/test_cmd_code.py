"""Tests for cmd_code module."""

from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pytest
from gitspaces.modules.cmd_code import code_command


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_with_space(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command with specified space."""
    # Setup mocks
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    # Create a real project path for workspace file creation
    project_path = tmp_path / "project"
    project_path.mkdir()
    space_path = project_path / "main"
    space_path.mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project.zzz_dir = project_path / ".zzz"
    mock_project_cls.find_project.return_value = mock_project

    args = Mock()
    args.space = "main"

    with patch("gitspaces.modules.cmd_code.runshell.subprocess.run") as mock_run:
        code_command(args)

        mock_run.assert_called_once()
        # Verify workspace file was opened instead of folder
        call_args = mock_run.call_args[0][0]
        assert ".code-workspace" in str(call_args[1])


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_no_project(mock_project_cls, mock_config_cls, mock_console):
    """Test code command when not in a project."""
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    mock_project_cls.find_project.return_value = None

    args = Mock()
    args.space = "main"

    with patch("gitspaces.modules.cmd_code.Path.cwd") as mock_cwd:
        mock_cwd.return_value = Path("/some/path")
        code_command(args)

    mock_console.println.assert_called_with("✗ Not in a GitSpaces project directory")


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_space_not_found(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command when space doesn't exist."""
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    project_path = tmp_path / "project"
    project_path.mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project_cls.find_project.return_value = mock_project

    args = Mock()
    args.space = "nonexistent"

    code_command(args)

    mock_console.println.assert_called_with("✗ Space 'nonexistent' not found")


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_editor_not_found(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command when editor is not found."""
    mock_config = Mock()
    mock_config.default_editor = "nonexistent-editor"
    mock_config_cls.instance.return_value = mock_config

    project_path = tmp_path / "project"
    project_path.mkdir()
    space_path = project_path / "main"
    space_path.mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project.zzz_dir = project_path / ".zzz"
    mock_project_cls.find_project.return_value = mock_project

    args = Mock()
    args.space = "main"

    with patch("gitspaces.modules.cmd_code.runshell.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
        code_command(args)

    mock_console.println.assert_any_call("✗ Editor 'nonexistent-editor' not found")


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_editor_error(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command when editor fails."""
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    project_path = tmp_path / "project"
    project_path.mkdir()
    space_path = project_path / "main"
    space_path.mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project.zzz_dir = project_path / ".zzz"
    mock_project_cls.find_project.return_value = mock_project

    args = Mock()
    args.space = "main"

    with patch("gitspaces.modules.cmd_code.runshell.subprocess.run") as mock_run:
        mock_run.side_effect = RuntimeError("Editor failed")
        with pytest.raises(RuntimeError):
            code_command(args)


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_select_space(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command with space selection."""
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "main").mkdir()
    (project_path / "feature").mkdir()
    zzz_dir = project_path / ".zzz"
    zzz_dir.mkdir()
    (zzz_dir / "sleep1").mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project.zzz_dir = zzz_dir
    mock_project.list_spaces.return_value = ["main", "feature", ".zzz/sleep1"]
    mock_project_cls.find_project.return_value = mock_project

    mock_console.prompt_select.return_value = "main"

    args = Mock()
    args.space = None

    # Patch Path.cwd to return a path outside any space
    with patch("gitspaces.modules.cmd_code.Path.cwd") as mock_cwd:
        mock_cwd.return_value = project_path
        with patch("gitspaces.modules.cmd_code.runshell.subprocess.run") as mock_run:
            code_command(args)

            mock_console.prompt_select.assert_called_once()
            mock_run.assert_called_once()


@patch("gitspaces.modules.cmd_code.Console")
@patch("gitspaces.modules.cmd_code.Config")
@patch("gitspaces.modules.cmd_code.Project")
def test_code_command_no_active_spaces(mock_project_cls, mock_config_cls, mock_console, tmp_path):
    """Test code command when no active spaces available."""
    mock_config = Mock()
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    project_path = tmp_path / "project"
    project_path.mkdir()
    zzz_dir = project_path / ".zzz"
    zzz_dir.mkdir()

    mock_project = Mock()
    mock_project.path = project_path
    mock_project.name = "project"
    mock_project.zzz_dir = zzz_dir
    mock_project.list_spaces.return_value = [".zzz/sleep1", ".zzz/sleep2"]
    mock_project_cls.find_project.return_value = mock_project

    args = Mock()
    args.space = None

    with patch("gitspaces.modules.cmd_code.Path.cwd") as mock_cwd:
        mock_cwd.return_value = project_path
        code_command(args)

    mock_console.println.assert_called_with("✗ No active spaces available")
