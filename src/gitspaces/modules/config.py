"""Configuration management for GitSpaces."""

import os
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any


class Config:
    """GitSpaces configuration management."""
    
    _instance: Optional['Config'] = None
    _config_dir: Optional[Path] = None
    _config_file: Optional[Path] = None
    _data: Dict[str, Any] = {}
    
    @classmethod
    def instance(cls) -> 'Config':
        """Get the singleton instance of Config."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        if self._config_dir is None:
            home = Path.home()
            self._config_dir = home / ".gitspaces"
        return self._config_dir
    
    @property
    def config_file(self) -> Path:
        """Get the configuration file path."""
        if self._config_file is None:
            self._config_file = self.config_dir / "config.yaml"
        return self._config_file
    
    @property
    def project_paths(self) -> List[str]:
        """Get the list of project paths."""
        return self._data.get('project_paths', [])
    
    @project_paths.setter
    def project_paths(self, paths: List[str]):
        """Set the list of project paths."""
        self._data['project_paths'] = paths
    
    @property
    def default_editor(self) -> str:
        """Get the default editor."""
        return self._data.get('default_editor', 'code')
    
    @default_editor.setter
    def default_editor(self, editor: str):
        """Set the default editor."""
        self._data['default_editor'] = editor

    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self._data = yaml.safe_load(f) or {}
        else:
            self._data = {}
    
    def save(self):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(self._data, f, default_flow_style=False)
    
    def exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_file.exists()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._data[key] = value


def init_config():
    """Initialize the configuration system."""
    config = Config.instance()
    config.load()


def run_user_environment_checks() -> bool:
    """Run user environment checks and setup if needed.
    
    Returns:
        True if environment is ready, False otherwise.
    """
    config = Config.instance()
    
    # Check if config exists
    if not config.exists():
        from gitspaces.modules.cmd_setup import run_setup
        return run_setup()
    
    # Check if project paths are configured
    if not config.project_paths:
        from gitspaces.modules.cmd_setup import run_setup
        return run_setup()
    
    return True
