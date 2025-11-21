"""Tests for path utilities."""

import pytest
from pathlib import Path
from gitspaces.modules.path import ensure_dir, expand_path, join_paths


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
