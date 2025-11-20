"""Git operations wrapper for GitSpaces."""

from pathlib import Path
from typing import Optional
from git import Repo
from gitspaces.modules.errors import GitSpacesError


def clone(url: str, target_path: str) -> None:
    """Clone a git repository.
    
    Args:
        url: Git repository URL
        target_path: Where to clone the repository
        
    Raises:
        GitSpacesError: If clone fails
    """
    try:
        Repo.clone_from(url, target_path)
    except Exception as e:
        raise GitSpacesError(f"Failed to clone repository: {e}")


def get_repo(path: str) -> Optional[Repo]:
    """Get a Repo instance for a path.
    
    Args:
        path: Path to git repository
        
    Returns:
        Repo instance or None if path doesn't exist
    """
    p = Path(path)
    if p.exists():
        try:
            return Repo(path)
        except Exception:
            return None
    return None


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
