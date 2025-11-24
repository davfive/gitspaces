"""Tests for CLI module."""

import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from gitspaces.cli import create_parser, main


def test_create_parser():
    """Test parser creation."""
    parser = create_parser()
    assert parser.prog == "gitspaces"


def test_parser_version(capsys):
    """Test --version argument."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])


def test_parser_debug():
    """Test --debug argument."""
    parser = create_parser()
    args = parser.parse_args(["--debug"])
    assert args.debug is True


def test_parser_clone_command():
    """Test clone command arguments."""
    parser = create_parser()
    args = parser.parse_args(["clone", "https://github.com/test/repo.git"])
    assert args.command == "clone"
    assert args.url == "https://github.com/test/repo.git"
    assert args.num_spaces == 3


def test_parser_clone_with_options():
    """Test clone command with options."""
    parser = create_parser()
    args = parser.parse_args(
        ["clone", "https://github.com/test/repo.git", "-n", "5", "-d", "/tmp/test"]
    )
    assert args.num_spaces == 5
    assert args.directory == "/tmp/test"


def test_parser_switch_command():
    """Test switch command."""
    parser = create_parser()
    args = parser.parse_args(["switch", "main"])
    assert args.command == "switch"
    assert args.space == "main"


def test_parser_sleep_command():
    """Test sleep command."""
    parser = create_parser()
    args = parser.parse_args(["sleep", "feature"])
    assert args.command == "sleep"
    assert args.space == "feature"


def test_parser_rename_command():
    """Test rename command."""
    parser = create_parser()
    args = parser.parse_args(["rename", "old", "new"])
    assert args.command == "rename"
    assert args.old_name == "old"
    assert args.new_name == "new"


def test_parser_code_command():
    """Test code command."""
    parser = create_parser()
    args = parser.parse_args(["code", "main"])
    assert args.command == "code"
    assert args.space == "main"


def test_parser_config_command():
    """Test config command."""
    parser = create_parser()
    args = parser.parse_args(["config", "key", "value"])
    assert args.command == "config"
    assert args.key == "key"
    assert args.value == "value"


def test_parser_extend_command():
    """Test extend command."""
    parser = create_parser()
    args = parser.parse_args(["extend", "-n", "2", "main"])
    assert args.command == "extend"
    assert args.num_spaces == 2
    assert args.space == "main"


def test_parser_setup_command():
    """Test setup command."""
    parser = create_parser()
    args = parser.parse_args(["setup"])
    assert args.command == "setup"


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
@patch("gitspaces.cli.Console")
def test_main_with_debug(mock_console, mock_checks, mock_init, monkeypatch):
    """Test main with debug flag."""
    mock_checks.return_value = True
    monkeypatch.setattr(sys, "argv", ["gitspaces", "--debug", "setup"])

    mock_func = Mock()
    with patch("gitspaces.cli.create_parser") as mock_parser:
        parser = MagicMock()
        args = MagicMock()
        args.debug = True
        args.command = "setup"
        args.func = mock_func
        parser.parse_args.return_value = args
        mock_parser.return_value = parser

        main()

        mock_console.println.assert_any_call(f"Args: {sys.argv}")
        mock_func.assert_called_once()


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
def test_main_config_error(mock_checks, mock_init, monkeypatch, capsys):
    """Test main when config initialization fails."""
    mock_init.side_effect = Exception("Config error")
    monkeypatch.setattr(sys, "argv", ["gitspaces", "setup"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
def test_main_environment_check_fails(mock_checks, mock_init, monkeypatch):
    """Test main when environment checks fail."""
    mock_checks.return_value = False
    monkeypatch.setattr(sys, "argv", ["gitspaces", "setup"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
@patch("gitspaces.modules.cmd_switch.switch_command")
def test_main_no_command_defaults_to_switch(mock_switch, mock_checks, mock_init, monkeypatch):
    """Test main defaults to switch when no command provided."""
    mock_checks.return_value = True
    monkeypatch.setattr(sys, "argv", ["gitspaces"])

    main()

    mock_switch.assert_called_once()


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
def test_main_keyboard_interrupt(mock_checks, mock_init, monkeypatch):
    """Test main handles keyboard interrupt."""
    mock_checks.return_value = True
    monkeypatch.setattr(sys, "argv", ["gitspaces", "setup"])

    mock_func = Mock(side_effect=KeyboardInterrupt())
    with patch("gitspaces.cli.create_parser") as mock_parser:
        parser = MagicMock()
        args = MagicMock()
        args.debug = False
        args.command = "setup"
        args.func = mock_func
        parser.parse_args.return_value = args
        mock_parser.return_value = parser

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
def test_main_user_aborted(mock_checks, mock_init, monkeypatch):
    """Test main handles user abort exception."""
    mock_checks.return_value = True
    monkeypatch.setattr(sys, "argv", ["gitspaces", "setup"])

    mock_func = Mock(side_effect=Exception("user aborted"))
    with patch("gitspaces.cli.create_parser") as mock_parser:
        parser = MagicMock()
        args = MagicMock()
        args.debug = False
        args.command = "setup"
        args.func = mock_func
        parser.parse_args.return_value = args
        mock_parser.return_value = parser

        # User aborted doesn't raise SystemExit, just returns
        main()


@patch("gitspaces.cli.init_config")
@patch("gitspaces.cli.run_user_environment_checks")
def test_main_general_exception(mock_checks, mock_init, monkeypatch):
    """Test main handles general exceptions."""
    mock_checks.return_value = True
    monkeypatch.setattr(sys, "argv", ["gitspaces", "setup"])

    mock_func = Mock(side_effect=Exception("Something went wrong"))
    with patch("gitspaces.cli.create_parser") as mock_parser:
        parser = MagicMock()
        args = MagicMock()
        args.debug = False
        args.command = "setup"
        args.func = mock_func
        parser.parse_args.return_value = args
        mock_parser.return_value = parser

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
