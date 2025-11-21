"""Space management for GitSpaces."""

from pathlib import Path
from typing import Optional
from git import Repo
from gitspaces.modules.errors import SpaceError
from gitspaces.modules.path import ensure_dir
from gitspaces.modules import runshell


class Space:
    """Represents a single workspace (clone) within a GitSpaces project."""

    def __init__(self, project, path: str):
        """Initialize a Space.

        Args:
            project: The parent Project instance.
            path: The path to the space directory.
        """
        self.project = project
        self.path = Path(path)
        self.name = self.path.name
        self._repo: Optional[Repo] = None

    @property
    def repo(self) -> Optional[Repo]:
        """Get the git repository for this space.

        Returns:
            The GitPython Repo instance or None.
        """
        if self._repo is None:
            self._repo = runshell.git.get_repo(str(self.path))
        return self._repo

    @classmethod
    def create_space_from_url(cls, project, url: str, path: str) -> "Space":
        """Create a new space by cloning from a URL.

        Args:
            project: The parent Project instance.
            url: The git repository URL.
            path: The path where the space will be created.

        Returns:
            The created Space instance.
        """
        if Path(path).exists():
            raise SpaceError(f"Space directory already exists: {path}")

        runshell.git.clone(url, path)
        space = cls(project, path)
        return space

    def duplicate(self) -> "Space":
        """Duplicate this space to a new sleeper space.

        Returns:
            The new Space instance.
        """
        new_path = self.project._get_empty_sleeper_path()

        try:
            # Copy the entire directory
            runshell.fs.copy_tree(str(self.path), new_path, symlinks=True)
        except Exception as e:
            raise SpaceError(f"Failed to duplicate space: {e}")

        return Space(self.project, new_path)

    def wake(self, new_name: Optional[str] = None) -> "Space":
        """Wake up a sleeping space and optionally rename it.

        Args:
            new_name: Optional new name for the space.

        Returns:
            The woken Space instance (may be a new instance if renamed).
        """
        # Check if this is a sleeping space
        if not str(self.path).startswith(str(self.project.zzz_dir)):
            raise SpaceError("Space is not sleeping")

        # Determine the new path
        if new_name:
            new_path = self.project.path / new_name
        else:
            # Use the default branch name or 'main'
            repo = self.repo
            if repo:
                branch_name = runshell.git.get_active_branch(repo)
            else:
                branch_name = "main"
            new_path = self.project.path / branch_name

        if new_path.exists():
            raise SpaceError(f"Target directory already exists: {new_path}")

        # Move the space
        runshell.fs.move(str(self.path), str(new_path))

        return Space(self.project, str(new_path))

    def sleep(self) -> "Space":
        """Put this space to sleep (move to .zzz directory).

        Returns:
            The sleeping Space instance.
        """
        # Check if already sleeping
        if str(self.path).startswith(str(self.project.zzz_dir)):
            raise SpaceError("Space is already sleeping")

        new_path = self.project._get_empty_sleeper_path()

        # Move the space
        runshell.fs.move(str(self.path), new_path)

        return Space(self.project, new_path)

    def rename(self, new_name: str) -> "Space":
        """Rename this space.

        Args:
            new_name: The new name for the space.

        Returns:
            The renamed Space instance.
        """
        # Check if sleeping
        if str(self.path).startswith(str(self.project.zzz_dir)):
            new_path = self.project.zzz_dir / new_name
        else:
            new_path = self.project.path / new_name

        if new_path.exists():
            raise SpaceError(f"Target directory already exists: {new_path}")

        # Rename the space
        runshell.fs.move(str(self.path), str(new_path))

        return Space(self.project, str(new_path))

    def get_current_branch(self) -> str:
        """Get the current branch name.

        Returns:
            The current branch name or "detached".
        """
        repo = self.repo
        if repo:
            return runshell.git.get_active_branch(repo)
        return "detached"

    def is_sleeping(self) -> bool:
        """Check if this space is sleeping.

        Returns:
            True if the space is in the .zzz directory.
        """
        return str(self.path).startswith(str(self.project.zzz_dir))
