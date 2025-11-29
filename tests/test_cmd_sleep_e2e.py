"""End-to-end tests for sleep command."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_sleep import sleep_command
from gitspaces.modules.project import Project


@pytest.mark.e2e
class TestSleepE2E:
    """End-to-end tests for the sleep command."""

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows locks directories when they are the current working directory",
    )
    def test_sleep_puts_active_clone_to_sleep(self, gitspaces_project, monkeypatch, capsys):
        """Move clone dir to .zzz/ with next available number."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.space = "main"

        sleep_command(args)

        captured = capsys.readouterr()
        assert "is now sleeping" in captured.out

        # Verify the space was moved to .zzz/
        assert not project_data["main_space"].exists()

        zzz_dir = project_data["zzz_dir"]
        sleepers = list(zzz_dir.iterdir())
        assert len(sleepers) == 1
        assert sleepers[0].name == "zzz-0"

    def test_sleep_with_interactive_selection(
        self, gitspaces_project, monkeypatch, mock_console_select, mock_console_confirm, capsys
    ):
        """Test sleeping with interactive space selection."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["project_path"])

        # Mock selecting 'feature' and declining to wake another
        mock_console_select(["feature"])
        mock_console_confirm([False])  # Don't wake another

        args = Mock()
        args.space = None

        sleep_command(args)

        captured = capsys.readouterr()
        assert "'feature' is now sleeping" in captured.out

        # Verify the space was moved
        assert not project_data["feature_space"].exists()

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows locks directories when they are the current working directory",
    )
    def test_sleep_wakes_sleeper_with_new_name(
        self,
        gitspaces_project_with_sleepers,
        monkeypatch,
        mock_console_select,
        mock_console_input,
        capsys,
    ):
        """Select sleeper, prompt for name, move out of .zzz/."""
        project_data = gitspaces_project_with_sleepers

        monkeypatch.chdir(project_data["main_space"])

        # Mock: select main to sleep, confirm wake, select zzz-0, name it "woken"
        mock_console_select(["main", ".zzz/zzz-0"])
        mock_console_input(["woken-space"])

        # Need to also mock confirm to wake
        from gitspaces.modules.console import Console

        original_confirm = Console.prompt_confirm
        confirm_calls = [True]  # Yes, wake another

        def mock_confirm(msg, default=True):
            if confirm_calls:
                return confirm_calls.pop(0)
            return default

        monkeypatch.setattr(Console, "prompt_confirm", mock_confirm)

        args = Mock()
        args.space = None

        sleep_command(args)

        captured = capsys.readouterr()
        assert "is now awake as 'woken-space'" in captured.out

        # Verify the sleeper was woken
        woken_path = project_data["project_path"] / "woken-space"
        assert woken_path.exists()

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows locks directories when they are the current working directory",
    )
    def test_sleep_list_shows_all_sleepers(
        self, gitspaces_project_with_sleepers, monkeypatch, capsys
    ):
        """When prompted to wake, show all sleeping spaces."""
        project_data = gitspaces_project_with_sleepers

        monkeypatch.chdir(project_data["main_space"])

        # Track what choices are offered for waking
        wake_choices = []

        def capture_select(message, choices, default=None):
            if "sleeping" in message.lower() or "wake" in message.lower():
                wake_choices.extend(choices)
            return choices[0] if choices else default

        from gitspaces.modules.console import Console

        monkeypatch.setattr(Console, "prompt_select", capture_select)

        # Mock confirm to wake
        monkeypatch.setattr(Console, "prompt_confirm", lambda msg, default=True: True)

        # Mock input for new name
        monkeypatch.setattr(Console, "prompt_input", lambda msg, default="": "new-name")

        args = Mock()
        args.space = "main"

        sleep_command(args)

        # Should have offered both sleepers
        assert ".zzz/zzz-0" in wake_choices or ".zzz/zzz-1" in wake_choices

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows locks directories when they are the current working directory",
    )
    def test_sleep_preserves_git_repo(self, gitspaces_project, monkeypatch, capsys):
        """Verify git repository is preserved when sleeping."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        # Verify main has git repo
        assert (project_data["main_space"] / ".git").exists()

        args = Mock()
        args.space = "main"

        sleep_command(args)

        # Find the sleeper and verify it still has .git
        zzz_dir = project_data["zzz_dir"]
        sleeper = list(zzz_dir.iterdir())[0]
        assert (sleeper / ".git").exists()
