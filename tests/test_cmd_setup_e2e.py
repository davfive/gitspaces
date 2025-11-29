"""End-to-end tests for setup command."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import Mock
import pytest
import yaml
from gitspaces.modules.cmd_setup import setup_command, run_setup
from gitspaces.modules.config import Config


@pytest.mark.e2e
class TestSetupE2E:
    """End-to-end tests for the setup command."""

    def test_setup_creates_config_file(
        self, temp_home, monkeypatch, mock_console_input, capsys
    ):
        """Creates ~/.gitspaces/config.yaml with project_dirs."""
        # Reset config singleton
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        project_dir = temp_home / "my-projects"

        # Mock inputs: project path, empty to finish, editor
        mock_console_input([str(project_dir), "", "vim"])

        # Mock confirm for creating directory
        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_confirm", lambda msg, default=True: True)

        args = Mock()

        setup_command(args)

        captured = capsys.readouterr()
        assert "Setup complete" in captured.out

        # Verify config file exists
        config_file = temp_home / ".gitspaces" / "config.yaml"
        assert config_file.exists()

        # Verify content
        with open(config_file) as f:
            config_data = yaml.safe_load(f)

        assert "project_paths" in config_data
        assert str(project_dir) in config_data["project_paths"]
        assert config_data["default_editor"] == "vim"

    def test_setup_prompts_for_editor(
        self, temp_home, monkeypatch, mock_console_input, capsys
    ):
        """Allow user to configure default editor."""
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        project_dir = temp_home / "projects"
        project_dir.mkdir()

        # Mock inputs: project path (existing), empty to finish, editor
        mock_console_input([str(project_dir), "", "nvim"])

        result = run_setup()

        assert result is True

        config = Config.instance()
        config.load()
        assert config.default_editor == "nvim"

    def test_setup_validates_directory_paths(
        self, temp_home, monkeypatch, capsys
    ):
        """Reject invalid/non-existent directories (unless user confirms creation)."""
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        nonexistent = temp_home / "does-not-exist"
        existing = temp_home / "existing"
        existing.mkdir()

        input_responses = [str(nonexistent), str(existing), "", "code"]
        input_iter = iter(input_responses)

        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_input", lambda msg, default="": next(input_iter, default))

        # First prompt for nonexistent - decline creation, then accept existing
        confirm_responses = [False]  # Don't create nonexistent
        confirm_iter = iter(confirm_responses)
        monkeypatch.setattr(Console, "prompt_confirm", lambda msg, default=True: next(confirm_iter, default))

        result = run_setup()

        assert result is True

        # Only existing path should be in config
        config = Config.instance()
        config.load()
        assert str(existing) in config.project_paths
        assert str(nonexistent) not in config.project_paths

    def test_setup_creates_directories_when_confirmed(
        self, temp_home, monkeypatch, mock_console_input, capsys
    ):
        """Create directories when user confirms."""
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        new_dir = temp_home / "new-projects-dir"
        assert not new_dir.exists()

        mock_console_input([str(new_dir), "", "code"])

        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_confirm", lambda msg, default=True: True)

        result = run_setup()

        assert result is True
        assert new_dir.exists()

    def test_setup_requires_at_least_one_path(
        self, temp_home, monkeypatch, capsys
    ):
        """At least one project path is required."""
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        project_dir = temp_home / "projects"
        project_dir.mkdir()

        # First try empty, then provide a valid path
        input_responses = ["", str(project_dir), "", "code"]
        input_iter = iter(input_responses)

        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_input", lambda msg, default="": next(input_iter, default))

        result = run_setup()

        assert result is True

        captured = capsys.readouterr()
        assert "At least one project path is required" in captured.out

    def test_setup_multiple_project_paths(
        self, temp_home, monkeypatch, mock_console_input, capsys
    ):
        """Support configuring multiple project directories."""
        Config._instance = None
        Config._config_dir = None
        Config._config_file = None
        Config._data = {}

        path1 = temp_home / "projects1"
        path2 = temp_home / "projects2"
        path1.mkdir()
        path2.mkdir()

        mock_console_input([str(path1), str(path2), "", "code"])

        result = run_setup()

        assert result is True

        config = Config.instance()
        config.load()
        assert len(config.project_paths) == 2
        assert str(path1) in config.project_paths
        assert str(path2) in config.project_paths
