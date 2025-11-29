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


def shell_targets_dir() -> Path:
    """Get the directory where shell target PID files are stored.

    Returns:
        The Path to the shell targets directory (~/.gitspaces/).
    """
    return Path.home() / ".gitspaces"


def write_shell_target(target_path: str | Path) -> bool:
    """Write the shell target file for the current process.

    This writes the target path to ~/.gitspaces/pid-{PID} so that
    the shell wrapper can read it and cd to that directory.

    Args:
        target_path: The path that the shell should cd to.

    Returns:
        True if the file was written successfully, False otherwise.
    """
    try:
        targets_dir = shell_targets_dir()
        targets_dir.mkdir(parents=True, exist_ok=True)

        pid = os.getpid()
        pid_file = targets_dir / f"pid-{pid}"
        pid_file.write_text(str(target_path))
        return True
    except (OSError, IOError):
        # Silently fail if we can't write the PID file
        # The shell wrapper will simply not cd, which is acceptable
        return False
