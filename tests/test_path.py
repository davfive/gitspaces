"""Tests for path utilities."""

import os
import pytest
from pathlib import Path
from gitspaces.modules.path import (
    ensure_dir,
    expand_path,
    join_paths,
    shell_targets_dir,
    write_shell_target,
)


def test_ensure_dir(tmp_path):
    """Test directory creation."""
    test_dir = tmp_path / "test" / "nested" / "dir"

    # Should create directory
    result = ensure_dir(test_dir)

    assert result.exists()
    assert result.is_dir()
    assert result == test_dir


def test_ensure_dir_existing(tmp_path):
    """Test ensure_dir with existing directory."""
    test_dir = tmp_path / "existing"
    test_dir.mkdir()

    # Should not raise error
    result = ensure_dir(test_dir)

    assert result.exists()
    assert result.is_dir()


def test_expand_path(monkeypatch):
    """Test path expansion."""
    monkeypatch.setenv("TEST_VAR", "/test/value")

    # Test home directory expansion
    result = expand_path("~/test")
    assert "~" not in result
    assert result.endswith("test")

    # Test environment variable expansion
    result = expand_path("$TEST_VAR/path")
    assert "TEST_VAR" not in result
    assert "/test/value/path" in result


def test_join_paths():
    """Test path joining."""
    result = join_paths("path", "to", "file.txt")

    assert "path" in result
    assert "to" in result
    assert "file.txt" in result


def test_shell_targets_dir():
    """Test shell_targets_dir returns correct path."""
    result = shell_targets_dir()

    assert result == Path.home() / ".gitspaces"
    assert isinstance(result, Path)


def test_write_shell_target(temp_home, monkeypatch):
    """Test write_shell_target writes correct PID file."""
    target_path = "/some/target/path"
    pid = os.getpid()

    write_shell_target(target_path)

    # Check the file was created
    pid_file = temp_home / ".gitspaces" / f"pid-{pid}"
    assert pid_file.exists()

    # Check the content
    content = pid_file.read_text()
    assert content == target_path

    # Cleanup
    pid_file.unlink()


def test_write_shell_target_with_path_object(temp_home, monkeypatch):
    """Test write_shell_target works with Path objects."""
    target_path = Path("/some/target/path")
    pid = os.getpid()

    write_shell_target(target_path)

    # Check the file was created
    pid_file = temp_home / ".gitspaces" / f"pid-{pid}"
    assert pid_file.exists()

    # Check the content
    content = pid_file.read_text()
    assert content == str(target_path)

    # Cleanup
    pid_file.unlink()
