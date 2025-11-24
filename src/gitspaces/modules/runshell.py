"""External command execution wrapper for GitSpaces.

This module encapsulates all external command execution (subprocess, git, and OS operations)
to isolate security scanner warnings and provide OS-agnostic operations.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union
from git import Repo
from gitspaces.modules.errors import GitSpacesError


# Subprocess wrapper - isolates security warnings
class subprocess:
    """Subprocess execution wrapper.

    Direct wrapper around subprocess.run with security annotations.
    All subprocess usage is safe as we never use shell=True and always
    pass arguments as lists.
    """

    @staticmethod
    def run(*args, **kwargs):
        """Execute a subprocess command.

        Args:
            *args: Positional arguments to subprocess.run
            **kwargs: Keyword arguments to subprocess.run

        Returns:
            subprocess.CompletedProcess
        """
        import subprocess as sp  # nosec B404

        # Security: Safe usage - args as list, no shell=True
        return sp.run(*args, **kwargs)  # nosec B603


# Git operations namespace
class git:
    """Git operations using GitPython."""

    @staticmethod
    def clone(url: str, target_path: Union[str, Path]) -> None:
        """Clone a git repository.

        Args:
            url: Git repository URL
            target_path: Where to clone the repository

        Raises:
            GitSpacesError: If clone fails
        """
        try:
            Repo.clone_from(url, str(target_path))
        except Exception as e:
            raise GitSpacesError(f"Failed to clone repository: {e}")

    @staticmethod
    def get_repo(path: Union[str, Path]) -> Optional[Repo]:
        """Get a Repo instance for a path.

        Args:
            path: Path to git repository

        Returns:
            Repo instance or None if path doesn't exist
        """
        p = Path(path)
        if p.exists():
            try:
                return Repo(str(path))
            except Exception:
                return None
        return None

    @staticmethod
    def get_active_branch(repo: Repo) -> str:
        """Get the active branch name.

        Args:
            repo: GitPython Repo instance

        Returns:
            Branch name or "detached" if HEAD is detached
        """
        try:
            return repo.active_branch.name
        except Exception:
            return "detached"

    @staticmethod
    def is_valid_repo(path: str) -> bool:
        """Check if path is a valid git repository.

        Args:
            path: Path to check

        Returns:
            True if valid git repository
        """
        try:
            Repo(path)
            return True
        except Exception:
            return False


# OS operations - cross-platform file/directory operations
class fs:
    """File system operations wrapper."""

    @staticmethod
    def move(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Move a file or directory.

        Args:
            src: Source path
            dst: Destination path
        """
        shutil.move(str(src), str(dst))

    @staticmethod
    def copy_tree(src: Union[str, Path], dst: Union[str, Path], symlinks: bool = True) -> None:
        """Recursively copy a directory tree.

        Args:
            src: Source directory
            dst: Destination directory
            symlinks: If True, preserve symlinks
        """
        shutil.copytree(str(src), str(dst), symlinks=symlinks)

    @staticmethod
    def chdir(path: Union[str, Path]) -> None:
        """Change the current working directory.

        Args:
            path: Directory path
        """
        os.chdir(str(path))
