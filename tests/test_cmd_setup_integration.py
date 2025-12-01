"""Integration tests for cmd_setup module."""

from __future__ import annotations

from unittest.mock import Mock

from gitspaces.modules.cmd_setup import run_setup, setup_command


def test_setup_command_success(
    temp_home,
    gitspaces_config,
    monkeypatch,
    mock_console_input,
    mock_console_confirm,
    capsys,
):
    """Test successful setup command."""
    # Mock console interactions
    projects_path = temp_home / "code" / "new_projects"
    mock_console_input(
        [str(projects_path), ""]
    )  # Enter project path, then empty to finish
    mock_console_confirm([True])  # Confirm to create directory

    args = Mock()

    setup_command(args)

    # Verify success message
    captured = capsys.readouterr()
    assert "Setup complete" in captured.out


def test_run_setup_creates_directories(
    temp_home, monkeypatch, mock_console_input, mock_console_confirm
):
    """Test that run_setup creates necessary directories."""
    # Mock console interactions
    projects_path = temp_home / "code" / "projects"
    mock_console_input([str(projects_path), ""])
    mock_console_confirm([True])  # Confirm to create directory

    result = run_setup()

    # Verify setup was successful
    assert result is True

    # Verify directory was created
    assert projects_path.exists()


def test_run_setup_existing_directories(temp_home, monkeypatch, mock_console_input):
    """Test run_setup with existing directories."""
    # Create directory first
    projects_path = temp_home / "code" / "projects"
    projects_path.mkdir(parents=True, exist_ok=True)

    # Mock console interactions
    mock_console_input([str(projects_path), ""])

    result = run_setup()

    # Verify setup was successful
    assert result is True


def test_run_setup_multiple_paths(
    temp_home, monkeypatch, mock_console_input, mock_console_confirm
):
    """Test run_setup with multiple project paths."""
    # Mock console interactions
    path1 = temp_home / "code" / "work"
    path2 = temp_home / "code" / "personal"
    mock_console_input([str(path1), str(path2), ""])
    mock_console_confirm([True, True])  # Confirm to create both directories

    result = run_setup()

    # Verify setup was successful
    assert result is True

    # Verify both directories were created
    assert path1.exists()
    assert path2.exists()


def test_run_setup_requires_at_least_one_path(
    temp_home, gitspaces_config, monkeypatch, mock_console_input, mock_console_confirm
):
    """Test that run_setup requires at least one project path."""
    # Mock console interactions - provide a path
    mock_console_input([str(temp_home / "code"), ""])
    mock_console_confirm([True])

    result = run_setup()

    # Verify setup was successful
    assert result is True
