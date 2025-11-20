"""Project management for GitSpaces."""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from git import Repo
from gitspaces.modules.errors import ProjectError
from gitspaces.modules.path import ensure_dir


class Project:
    """Represents a GitSpaces project containing multiple spaces."""
    
    DOTFILE = "__GITSPACES_PROJECT__"
    ZZZ_DIR = ".zzz"
    
    def __init__(self, path: str):
        """Initialize a Project.
        
        Args:
            path: The path to the project directory.
        """
        self.path = Path(path)
        self.name = self.path.name
        self.code_ws_dir = self.path / ".vscode"
        self.dotfile = self.path / self.DOTFILE
        self.zzz_dir = self.path / self.ZZZ_DIR
    
    @classmethod
    def create_project(cls, directory: str, url: str, num_spaces: int = 1) -> 'Project':
        """Create a new GitSpaces project.
        
        Args:
            directory: The directory where the project will be created.
            url: The git repository URL.
            num_spaces: The number of spaces to create.
            
        Returns:
            The created Project instance.
        """
        from .space import Space
        
        # Extract project name from URL
        project_name = cls._extract_project_name(url)
        project_path = Path(directory) / project_name
        
        if project_path.exists():
            raise ProjectError(f"Project directory already exists: {project_path}")
        
        # Create project instance and initialize
        project = cls(str(project_path))
        project._init()
        
        # Create first space from URL
        first_space = Space.create_space_from_url(project, url, project._get_empty_sleeper_path())
        
        # Duplicate for additional spaces
        for _ in range(1, num_spaces):
            first_space.duplicate()
        
        return project
    
    @staticmethod
    def _extract_project_name(url: str) -> str:
        """Extract project name from git URL.
        
        Args:
            url: The git repository URL.
            
        Returns:
            The project name.
        """
        # Remove .git suffix and extract last part of path
        name = url.rstrip('/').split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]
        return name
    
    def _init(self):
        """Initialize the project directory structure."""
        ensure_dir(self.path)
        ensure_dir(self.zzz_dir)
        self.dotfile.touch()
    
    def _get_empty_sleeper_path(self) -> str:
        """Get the path for a new sleeper space.
        
        Returns:
            The path for the new sleeper space.
        """
        # Find the next available zzz-N directory
        i = 0
        while True:
            sleeper_path = self.zzz_dir / f"zzz-{i}"
            if not sleeper_path.exists():
                return str(sleeper_path)
            i += 1
    
    def list_spaces(self) -> List[str]:
        """List all spaces in the project.
        
        Returns:
            List of space directory names.
        """
        spaces = []
        
        # List active spaces (top-level directories, excluding special ones)
        for item in self.path.iterdir():
            if item.is_dir() and item.name not in [self.ZZZ_DIR, '.vscode'] and not item.name.startswith('.'):
                if item.name != self.DOTFILE:
                    spaces.append(item.name)
        
        # List sleeping spaces
        if self.zzz_dir.exists():
            for item in self.zzz_dir.iterdir():
                if item.is_dir():
                    spaces.append(f"{self.ZZZ_DIR}/{item.name}")
        
        return sorted(spaces)
    
    def exists(self) -> bool:
        """Check if the project exists.
        
        Returns:
            True if the project directory and dotfile exist.
        """
        return self.path.exists() and self.dotfile.exists()
    
    @classmethod
    def find_project(cls, path: str) -> Optional['Project']:
        """Find a GitSpaces project by searching upward from the given path.
        
        Args:
            path: The path to start searching from.
            
        Returns:
            The Project instance if found, None otherwise.
        """
        current = Path(path).resolve()
        
        while current != current.parent:
            dotfile = current / cls.DOTFILE
            if dotfile.exists():
                return cls(str(current))
            current = current.parent
        
        return None
