"""End-to-end tests for extend command."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import Mock
import pytest
from gitspaces.modules.cmd_extend import extend_command
from gitspaces.modules.project import Project


@pytest.mark.e2e
class TestExtendE2E:
    """End-to-end tests for the extend command."""

    def test_extend_creates_new_sleeper_clone(self, gitspaces_project, monkeypatch, capsys):
        """Verify new .zzz-N directory created with git clone."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.num_spaces = 1
        args.space = None

        extend_command(args)

        # Verify sleeper was created
        zzz_dir = project_data["zzz_dir"]
        sleepers = list(zzz_dir.iterdir())
        assert len(sleepers) == 1

        # Verify it's a valid git repo
        sleeper_path = sleepers[0]
        assert (sleeper_path / ".git").exists()

    def test_extend_increments_sleeper_counter(self, gitspaces_project, monkeypatch, capsys):
        """New sleeper gets next available number."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        # Create first extension
        args = Mock()
        args.num_spaces = 1
        args.space = None

        extend_command(args)

        # Create second extension
        extend_command(args)

        # Verify sleepers were created with incrementing names
        zzz_dir = project_data["zzz_dir"]
        sleepers = sorted(zzz_dir.iterdir())
        assert len(sleepers) == 2

        # Check naming
        names = [s.name for s in sleepers]
        assert "zzz-0" in names
        assert "zzz-1" in names

    def test_extend_outputs_correct_help_message(self, gitspaces_project, monkeypatch, capsys):
        """Verify final message references 'gitspaces switch', not 'gitspaces sleep'."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.num_spaces = 1
        args.space = None

        extend_command(args)

        captured = capsys.readouterr()

        # Should mention 'gitspaces switch'
        assert "gitspaces switch" in captured.out
        # Should NOT mention 'gitspaces sleep'
        assert "gitspaces sleep" not in captured.out

    def test_extend_creates_multiple_clones(self, gitspaces_project, monkeypatch, capsys):
        """Test creating multiple clones at once."""
        project_data = gitspaces_project

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.num_spaces = 3
        args.space = None

        extend_command(args)

        captured = capsys.readouterr()

        # Verify 3 sleepers were created
        zzz_dir = project_data["zzz_dir"]
        sleepers = list(zzz_dir.iterdir())
        assert len(sleepers) == 3

        # Verify success message
        assert "Successfully created 3" in captured.out

    def test_extend_uses_current_space_as_source(self, gitspaces_project, monkeypatch, capsys):
        """When in a space, use that as the source for cloning."""
        project_data = gitspaces_project

        # Add a file to main space to verify it's used as source
        test_file = project_data["main_space"] / "test-marker.txt"
        test_file.write_text("marker")

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.num_spaces = 1
        args.space = None

        extend_command(args)

        captured = capsys.readouterr()
        assert "Using current space 'main'" in captured.out

        # Verify the marker file was copied
        zzz_dir = project_data["zzz_dir"]
        sleeper = list(zzz_dir.iterdir())[0]
        assert (sleeper / "test-marker.txt").exists()

    def test_extend_with_specific_source_space(self, gitspaces_project, monkeypatch, capsys):
        """Test extending from a specific named space."""
        project_data = gitspaces_project

        # Add a file to feature space
        test_file = project_data["feature_space"] / "feature-marker.txt"
        test_file.write_text("feature marker")

        monkeypatch.chdir(project_data["main_space"])

        args = Mock()
        args.num_spaces = 1
        args.space = "feature"

        extend_command(args)

        # Verify the marker file was copied
        zzz_dir = project_data["zzz_dir"]
        sleeper = list(zzz_dir.iterdir())[0]
        assert (sleeper / "feature-marker.txt").exists()
