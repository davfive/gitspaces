"""Error handling utilities."""


class GitSpacesError(Exception):
    """Base exception for GitSpaces errors."""

    pass


class ConfigError(GitSpacesError):
    """Configuration related errors."""

    pass


class ProjectError(GitSpacesError):
    """Project related errors."""

    pass


class SpaceError(GitSpacesError):
    """Space related errors."""

    pass
