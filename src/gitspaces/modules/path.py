"""Path utility functions."""

from __future__ import annotations

import os
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to ensure exists.

    Returns:
        The Path object for the directory.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def expand_path(path: str) -> str:
    """Expand user home directory and environment variables in path.

    Args:
        path: The path to expand.

    Returns:
        The expanded path as a string.
    """
    return os.path.expanduser(os.path.expandvars(path))


def join_paths(*paths: str) -> str:
    """Join multiple path components.

    Args:
        *paths: Path components to join.

    Returns:
        The joined path as a string.
    """
    return os.path.join(*paths)
