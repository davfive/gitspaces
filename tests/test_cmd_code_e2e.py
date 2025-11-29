"""End-to-end tests for code command."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from gitspaces.modules.cmd_code import code_command
from gitspaces.modules.project import Project


@pytest.mark.e2e
class TestCodeE2E:
    """End-to-end tests for the code command."""

    def test_code_uses_current_clone_when_inside_project(
        self, gitspaces_project, monkeypatch, capsys
    ):
        """When in clone dir, open that clone without prompting."""
        project_data = gitspaces_project

        # Change to main space
        monkeypatch.chdir(project_data["main_space"])

        # Track editor call
        editor_called_with = []

        from gitspaces.modules import runshell
        def mock_run(cmd, **kwargs):
            editor_called_with.append(cmd)

        monkeypatch.setattr(runshell.subprocess, "run", mock_run)

        args = Mock()
        args.space = None

        code_command(args)

        captured = capsys.readouterr()

        # Should open workspace for main without prompting
        assert "Opening 'main'" in captured.out
        assert len(editor_called_with) == 1
        assert ".code-workspace" in str(editor_called_with[0][1])

    def test_code_creates_workspace_file(
        self, gitspaces_project, monkeypatch
    ):
        """Generate .code-workspace/<project>~<clone>.code-workspace if missing."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        from gitspaces.modules import runshell
        monkeypatch.setattr(runshell.subprocess, "run", lambda cmd, **kwargs: None)

        args = Mock()
        args.space = "main"

        code_command(args)

        # Check workspace file exists
        ws_dir = project_data["project_path"] / ".code-workspace"
        assert ws_dir.exists()

        ws_files = list(ws_dir.glob("*.code-workspace"))
        assert len(ws_files) == 1

        # Verify workspace file name format
        ws_file = ws_files[0]
        assert "test-project~main" in ws_file.name

        # Verify content
        content = json.loads(ws_file.read_text())
        assert "folders" in content
        assert len(content["folders"]) == 1
        assert str(project_data["main_space"]) in content["folders"][0]["path"]

    def test_code_opens_workspace_not_folder(
        self, gitspaces_project, monkeypatch
    ):
        """Verify 'code' command receives .code-workspace file, not directory."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        editor_args = []

        from gitspaces.modules import runshell
        def mock_run(cmd, **kwargs):
            editor_args.extend(cmd)

        monkeypatch.setattr(runshell.subprocess, "run", mock_run)

        args = Mock()
        args.space = "main"

        code_command(args)

        # Verify workspace file was passed, not directory
        assert len(editor_args) == 2  # ['code', 'path/to/workspace.code-workspace']
        assert ".code-workspace" in editor_args[1]
        # Should not be the space directory itself
        assert not editor_args[1].endswith("/main")

    def test_code_prompts_when_outside_space(
        self, gitspaces_project, monkeypatch, mock_console_select, capsys
    ):
        """When not in a space, show selection list of all clones."""
        project_data = gitspaces_project

        # Change to project root (not inside a space)
        monkeypatch.chdir(project_data["project_path"])

        mock_console_select(["feature"])

        from gitspaces.modules import runshell
        monkeypatch.setattr(runshell.subprocess, "run", lambda cmd, **kwargs: None)

        args = Mock()
        args.space = None

        code_command(args)

        captured = capsys.readouterr()
        assert "Opening 'feature'" in captured.out

    def test_code_workspace_includes_correct_path(
        self, gitspaces_project, monkeypatch
    ):
        """Workspace file should include correct folder path."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["feature_space"])

        from gitspaces.modules import runshell
        monkeypatch.setattr(runshell.subprocess, "run", lambda cmd, **kwargs: None)

        args = Mock()
        args.space = "feature"

        code_command(args)

        # Check workspace file content
        ws_file = project_data["project_path"] / ".code-workspace" / "test-project~feature.code-workspace"
        assert ws_file.exists()

        content = json.loads(ws_file.read_text())
        folder_path = content["folders"][0]["path"]
        assert str(project_data["feature_space"]) == folder_path
