"""Tests for configuration module."""

import pytest
from pathlib import Path
from gitspaces.modules.config import Config, init_config


def test_config_singleton():
    """Test that Config is a singleton."""
    config1 = Config.instance()
    config2 = Config.instance()
    assert config1 is config2


def test_config_dir(tmp_path, monkeypatch):
    """Test configuration directory path."""
    # Reset singleton
    Config._instance = None

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Config.instance()

    expected_dir = tmp_path / ".gitspaces"
    assert config.config_dir == expected_dir


def test_config_file(tmp_path, monkeypatch):
    """Test configuration file path."""
    Config._instance = None

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Config.instance()

    expected_file = tmp_path / ".gitspaces" / "config.yaml"
    assert config.config_file == expected_file


def test_project_paths():
    """Test project paths property."""
    Config._instance = None
    config = Config.instance()

    # Default should be empty list
    assert config.project_paths == []

    # Set paths
    test_paths = ["/path/1", "/path/2"]
    config.project_paths = test_paths
    assert config.project_paths == test_paths


def test_default_editor():
    """Test default editor property."""
    Config._instance = None
    config = Config.instance()

    # Default should be 'code'
    assert config.default_editor == "code"

    # Set editor
    config.default_editor = "vim"
    assert config.default_editor == "vim"


def test_config_save_load(tmp_path, monkeypatch):
    """Test saving and loading configuration."""
    Config._instance = None

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Config.instance()

    # Set some values
    config.project_paths = ["/test/path1", "/test/path2"]
    config.default_editor = "emacs"

    # Save
    config.save()

    # Verify file exists
    assert config.config_file.exists()

    # Create new config and load
    Config._instance = None
    config2 = Config.instance()
    config2.load()

    # Verify values
    assert config2.project_paths == ["/test/path1", "/test/path2"]
    assert config2.default_editor == "emacs"


def test_config_get_set():
    """Test generic get/set methods."""
    Config._instance = None
    config = Config.instance()

    # Test set and get
    config.set("custom_key", "custom_value")
    assert config.get("custom_key") == "custom_value"

    # Test get with default
    assert config.get("nonexistent", "default") == "default"
