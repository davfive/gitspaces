"""End-to-end tests for clone command."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from gitspaces.modules.cmd_clone import clone_command
from gitspaces.modules.project import Project


@pytest.mark.e2e
class TestCloneE2E:
    """End-to-end tests for the clone command."""

    def test_clone_prompts_for_target_directory(
        self,
        bare_git_repo,
        gitspaces_config,
        monkeypatch,
        mock_console_select,
        mock_console_input,
    ):
        """User selects from configured project directories when multiple exist."""
        # Add another project path to config
        from gitspaces.modules.config import Config

        config = Config.instance()
        second_path = gitspaces_config["projects_dir"].parent / "second-dir"
        second_path.mkdir(parents=True, exist_ok=True)
        config.project_paths = [str(gitspaces_config["projects_dir"]), str(second_path)]

        # Mock to select first project path and space name
        mock_console_select([str(gitspaces_config["projects_dir"])])
        mock_console_input(["main"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.url = str(bare_git_repo)
        args.num_spaces = 2
        args.directory = None

        clone_command(args)

        # Verify project was created in selected path
        project_path = gitspaces_config["projects_dir"] / "bare-repo"
        assert project_path.exists()
        assert (project_path / Project.DOTFILE).exists()

    def test_clone_creates_project_structure(
        self, bare_git_repo, gitspaces_config, monkeypatch, mock_console_input
    ):
        """Creates project dir with marker, main clone, and N sleepers in .zzz/."""
        mock_console_input(["main"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.url = str(bare_git_repo)
        args.num_spaces = 3
        args.directory = str(gitspaces_config["projects_dir"])

        clone_command(args)

        project_path = gitspaces_config["projects_dir"] / "bare-repo"

        # Verify project structure
        assert project_path.exists()
        assert (project_path / Project.DOTFILE).exists()
        assert (project_path / ".zzz").exists()

        # Should have one woken space (main) and 2 sleepers
        assert (project_path / "main").exists()

        zzz_dir = project_path / ".zzz"
        sleepers = list(zzz_dir.iterdir())
        assert len(sleepers) == 2  # 3 total - 1 woken = 2 remaining sleepers

    def test_clone_wakes_one_sleeper_after_creation(
        self, bare_git_repo, gitspaces_config, monkeypatch, mock_console_input, capsys
    ):
        """After cloning, prompt user to name one sleeper and wake it."""
        mock_console_input(["my-first-space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.url = str(bare_git_repo)
        args.num_spaces = 2
        args.directory = str(gitspaces_config["projects_dir"])

        clone_command(args)

        project_path = gitspaces_config["projects_dir"] / "bare-repo"

        captured = capsys.readouterr()
        assert (
            "my-first-space" in captured.out
            or (project_path / "my-first-space").exists()
        )

    def test_clone_writes_path_for_shell_cd(
        self,
        bare_git_repo,
        gitspaces_config,
        monkeypatch,
        mock_console_input,
        shell_pid_file,
    ):
        """After waking sleeper, write path for shell wrapper to cd."""
        mock_console_input(["dev-space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.url = str(bare_git_repo)
        args.num_spaces = 2
        args.directory = str(gitspaces_config["projects_dir"])

        clone_command(args)

        # Check PID file was created
        assert shell_pid_file["file"].exists(), "PID file should be created"

        # Check content contains the new space path
        content = shell_pid_file["file"].read_text()
        assert "dev-space" in content
