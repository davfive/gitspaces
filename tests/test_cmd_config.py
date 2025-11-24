"""Tests for cmd_config module."""

from unittest.mock import Mock, patch
from gitspaces.modules.cmd_config import config_command


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_show_all(mock_config_cls, mock_console):
    """Test config command showing all configuration."""
    mock_config = Mock()
    mock_config.config_file = "/home/user/.config/gitspaces/config.yaml"
    mock_config.project_paths = ["/home/user/projects"]
    mock_config.default_editor = "code"
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = None

    config_command(args)

    mock_console.println.assert_any_call("GitSpaces Configuration")


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_get_value(mock_config_cls, mock_console):
    """Test config command getting a value."""
    mock_config = Mock()
    mock_config.get.return_value = "code"
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = "default_editor"
    args.value = None

    config_command(args)

    mock_config.get.assert_called_with("default_editor")
    mock_console.println.assert_called_with("default_editor: code")


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_get_nonexistent(mock_config_cls, mock_console):
    """Test config command getting nonexistent key."""
    mock_config = Mock()
    mock_config.get.return_value = None
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = "nonexistent"
    args.value = None

    config_command(args)

    mock_console.println.assert_called_with("✗ Configuration key 'nonexistent' not found")


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_set_value(mock_config_cls, mock_console):
    """Test config command setting a value."""
    mock_config = Mock()
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = "default_editor"
    args.value = "vim"

    config_command(args)

    mock_config.set.assert_called_with("default_editor", "vim")
    mock_config.save.assert_called_once()
    mock_console.println.assert_called_with("✓ Set default_editor = vim")


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_add_project_path(mock_config_cls, mock_console):
    """Test config command adding project path."""
    mock_config = Mock()
    mock_config.project_paths = ["/home/user/projects"]
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = "project_paths"
    args.value = "/home/user/newprojects"

    config_command(args)

    assert "/home/user/newprojects" in mock_config.project_paths
    mock_config.save.assert_called_once()
    mock_console.println.assert_called_with("✓ Added '/home/user/newprojects' to project_paths")


@patch("gitspaces.modules.cmd_config.Console")
@patch("gitspaces.modules.cmd_config.Config")
def test_config_command_add_existing_project_path(mock_config_cls, mock_console):
    """Test config command adding existing project path."""
    mock_config = Mock()
    mock_config.project_paths = ["/home/user/projects"]
    mock_config_cls.instance.return_value = mock_config

    args = Mock()
    args.key = "project_paths"
    args.value = "/home/user/projects"

    config_command(args)

    mock_console.println.assert_called_with("Path '/home/user/projects' already in project_paths")
