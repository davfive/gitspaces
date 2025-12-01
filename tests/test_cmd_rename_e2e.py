"""End-to-end tests for rename command."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from gitspaces.modules.cmd_rename import rename_command


@pytest.mark.e2e
class TestRenameE2E:
    """End-to-end tests for the rename command."""

    def test_rename_uses_current_clone_as_source(
        self, gitspaces_project, monkeypatch, capsys
    ):
        """When in clone dir, only require new_name argument."""
        project_data = gitspaces_project

        # Change to main space
        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        chdir_calls = []
        monkeypatch.setattr(runshell.fs, "chdir", lambda x: chdir_calls.append(x))

        args = Mock()
        args.old_name = "new-name"  # This will be treated as new_name when only one arg
        args.new_name = None

        rename_command(args)

        captured = capsys.readouterr()
        assert "Renamed space 'main' to 'new-name'" in captured.out

        # Verify directory was renamed
        assert not project_data["main_space"].exists()
        new_path = project_data["project_path"] / "new-name"
        assert new_path.exists()

    def test_rename_changes_directory_name(
        self, gitspaces_project, monkeypatch, capsys
    ):
        """Verify filesystem directory is renamed."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.old_name = "main"
        args.new_name = "renamed-space"

        rename_command(args)

        # Verify directory was renamed
        assert not project_data["main_space"].exists()
        new_path = project_data["project_path"] / "renamed-space"
        assert new_path.exists()

        # Verify git repo still works
        assert (new_path / ".git").exists()

    def test_rename_writes_new_path_for_shell_cd(
        self, gitspaces_project, monkeypatch, shell_pid_file, capsys
    ):
        """After rename, cd user into renamed directory."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.old_name = "main"
        args.new_name = "my-new-name"

        rename_command(args)

        # Check PID file was created
        assert shell_pid_file["file"].exists()

        # Check content
        content = shell_pid_file["file"].read_text()
        assert "my-new-name" in content

    def test_rename_with_both_arguments(self, gitspaces_project, monkeypatch, capsys):
        """Test rename when both old_name and new_name are provided."""
        project_data = gitspaces_project

        # Change to project root, not inside a space
        monkeypatch.chdir(project_data["project_path"])

        from gitspaces.modules import runshell

        monkeypatch.setattr(runshell.fs, "chdir", lambda x: None)

        args = Mock()
        args.old_name = "feature"
        args.new_name = "feature-v2"

        rename_command(args)

        captured = capsys.readouterr()
        assert "Renamed space 'feature' to 'feature-v2'" in captured.out

        # Verify directory was renamed
        assert not project_data["feature_space"].exists()
        new_path = project_data["project_path"] / "feature-v2"
        assert new_path.exists()

    def test_rename_prevents_overwrite(self, gitspaces_project, monkeypatch, capsys):
        """Test that rename fails if target name already exists."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.old_name = "main"
        args.new_name = "feature"  # Already exists

        rename_command(args)

        captured = capsys.readouterr()
        assert "already exists" in captured.out

        # Verify original directory still exists
        assert project_data["main_space"].exists()
