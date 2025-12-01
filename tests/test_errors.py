"""Tests for error classes."""

from gitspaces.modules.errors import (
    ConfigError,
    GitSpacesError,
    ProjectError,
    SpaceError,
)


def test_gitspaces_error():
    """Test GitSpacesError base exception."""
    error = GitSpacesError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_config_error():
    """Test ConfigError exception."""
    error = ConfigError("Config error")
    assert str(error) == "Config error"
    assert isinstance(error, GitSpacesError)


def test_project_error():
    """Test ProjectError exception."""
    error = ProjectError("Project error")
    assert str(error) == "Project error"
    assert isinstance(error, GitSpacesError)


def test_space_error():
    """Test SpaceError exception."""
    error = SpaceError("Space error")
    assert str(error) == "Space error"
    assert isinstance(error, GitSpacesError)
