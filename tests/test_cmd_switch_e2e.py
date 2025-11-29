"""End-to-end tests for switch command."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_switch import switch_command
from gitspaces.modules.project import Project
from gitspaces.modules.config import Config


@pytest.mark.e2e
class TestSwitchE2E:
    """End-to-end tests for the switch command."""

    def test_switch_from_outside_project_shows_all_projects(
        self, multiple_projects, monkeypatch, capsys
    ):
        """When not in any project, list all projects from config dirs."""
        # Initialize config with the project paths
        Config._instance = None
        config = Config.instance()
        config.project_paths = [str(multiple_projects["projects_dir"])]

        # Change to a directory outside any project
        monkeypatch.chdir(multiple_projects["projects_dir"])

        # Track what choices are offered
        choices_offered = []

        def capture_select(message, choices, default=None):
            choices_offered.extend(choices)
            return choices[0] if choices else default

        from gitspaces.modules.console import Console

        monkeypatch.setattr(Console, "prompt_select", capture_select)

        # Mock chdir
        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.space = None

        switch_command(args)

        # Should list all projects
        assert "project-alpha" in choices_offered

    def test_switch_hides_sleeper_clones(
        self, gitspaces_project_with_sleepers, monkeypatch, mock_console_input, capsys
    ):
        """Sleeper .zzz-* clones should not appear in the main list."""
        project_data = gitspaces_project_with_sleepers

        # Change to project directory (not inside a space)
        monkeypatch.chdir(project_data["project_path"])

        # Mock chdir
        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        # Track what choices are offered
        choices_offered = []

        def capture_select(message, choices, default=None):
            choices_offered.extend(choices)
            # Return the first non-wake option to avoid triggering wake flow
            for c in choices:
                if not c.startswith("Wake up"):
                    return c
            return choices[0] if choices else default

        from gitspaces.modules.console import Console

        monkeypatch.setattr(Console, "prompt_select", capture_select)

        args = Mock()
        args.space = None

        switch_command(args)

        # Verify sleepers are not in the main list (except in "Wake up" option)
        main_choices = [c for c in choices_offered if not c.startswith("Wake up")]
        for choice in main_choices:
            assert not choice.startswith(".zzz/"), f"Sleeper {choice} should not be in list"

    def test_switch_shows_wake_up_option_when_sleepers_exist(
        self, gitspaces_project_with_sleepers, monkeypatch, capsys
    ):
        """Show 'Wake up (N)' option when N sleepers exist."""
        project_data = gitspaces_project_with_sleepers

        monkeypatch.chdir(project_data["project_path"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        # Track what choices are offered
        choices_offered = []

        def capture_select(message, choices, default=None):
            choices_offered.extend(choices)
            # Return first non-wake option
            for c in choices:
                if not c.startswith("Wake up"):
                    return c
            return choices[0] if choices else default

        from gitspaces.modules.console import Console

        monkeypatch.setattr(Console, "prompt_select", capture_select)

        args = Mock()
        args.space = None

        switch_command(args)

        # Verify "Wake up" option is present
        wake_options = [c for c in choices_offered if c.startswith("Wake up")]
        assert len(wake_options) > 0, "Wake up option should be present"
        # Should include count of sleepers
        assert "2" in wake_options[0] or "sleeping" in wake_options[0]

    def test_switch_filters_current_clone_from_list(self, gitspaces_project, monkeypatch, capsys):
        """Current clone directory should not appear in selection."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        # Track what choices are offered
        choices_offered = []

        def capture_select(message, choices, default=None):
            choices_offered.extend(choices)
            return choices[0] if choices else default

        from gitspaces.modules.console import Console

        monkeypatch.setattr(Console, "prompt_select", capture_select)

        args = Mock()
        args.space = None

        switch_command(args)

        # Current directory is "main" - it should not be in choices
        assert "main" not in choices_offered, "Current space should not be in choices"
        assert "feature" in choices_offered, "Other spaces should be in choices"

    def test_switch_writes_target_path_for_shell_wrapper(
        self, gitspaces_project, monkeypatch, shell_pid_file
    ):
        """After selection, target path written to ~/.gitspaces/pid-{PID} file."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.space = "feature"

        switch_command(args)

        # Check PID file was created
        assert shell_pid_file["file"].exists(), "PID file should be created"

        # Check content
        content = shell_pid_file["file"].read_text()
        assert "feature" in content

    def test_switch_wakes_sleeper_when_selected(
        self, gitspaces_project_with_sleepers, monkeypatch, mock_console_input, capsys
    ):
        """Selecting sleeper prompts for name and wakes it."""
        project_data = gitspaces_project_with_sleepers

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        # Mock the input for new space name
        mock_console_input(["my-new-space"])

        args = Mock()
        args.space = ".zzz/zzz-0"

        switch_command(args)

        captured = capsys.readouterr()
        assert "Woke space" in captured.out

        # Verify the sleeper was moved
        assert not project_data["sleeper1"].exists()
        new_space = project_data["project_path"] / "my-new-space"
        assert new_space.exists()
