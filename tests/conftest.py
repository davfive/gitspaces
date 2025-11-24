"""Pytest configuration and fixtures for GitSpaces tests."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock
import pytest
import yaml
from git import Repo


@pytest.fixture
def temp_home(monkeypatch):
    """Create a temporary home directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_home_path = Path(temp_dir) / "home"
        temp_home_path.mkdir()
        
        # Set HOME environment variable
        monkeypatch.setenv("HOME", str(temp_home_path))
        monkeypatch.setenv("USERPROFILE", str(temp_home_path))  # For Windows
        
        yield temp_home_path


@pytest.fixture
def temp_git_repo(temp_home):
    """Create a temporary git repository for testing."""
    repo_path = temp_home / "test-repo"
    repo_path.mkdir()
    
    # Initialize git repo
    repo = Repo.init(repo_path)
    
    # Create initial commit
    readme = repo_path / "README.md"
    readme.write_text("# Test Repository\n")
    repo.index.add([str(readme)])
    repo.index.commit("Initial commit")
    
    return repo_path


@pytest.fixture
def gitspaces_config(temp_home, monkeypatch):
    """Create a GitSpaces configuration file."""
    config_dir = temp_home / ".gitspaces"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "config.yml"
    projects_dir = temp_home / "code" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    config_data = {
        "project_paths": [str(projects_dir)],
        "default_editor": "code"
    }
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    
    # Reset Config singleton
    from gitspaces.modules.config import Config
    Config._instance = None
    Config._config_dir = None
    Config._config_file = None
    Config._data = {}
    
    yield {
        "config_dir": config_dir,
        "config_file": config_file,
        "projects_dir": projects_dir
    }


@pytest.fixture
def gitspaces_project(temp_home, gitspaces_config, temp_git_repo):
    """Create a GitSpaces project with spaces."""
    from gitspaces.modules.project import Project
    
    projects_dir = gitspaces_config["projects_dir"]
    project_name = "test-project"
    project_path = projects_dir / project_name
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create project marker file
    dotfile = project_path / Project.DOTFILE
    dotfile.touch()
    
    # Create .zzz directory for sleeping spaces
    zzz_dir = project_path / Project.ZZZ_DIR
    zzz_dir.mkdir(exist_ok=True)
    
    # Create main space
    main_space = project_path / "main"
    main_space.mkdir(exist_ok=True)
    
    # Initialize as git repo
    repo = Repo.init(main_space)
    readme = main_space / "README.md"
    readme.write_text("# Test Project\n")
    repo.index.add([str(readme)])
    repo.index.commit("Initial commit")
    
    # Create feature space
    feature_space = project_path / "feature"
    shutil.copytree(main_space, feature_space)
    
    project = Project(str(project_path))
    
    yield {
        "project": project,
        "project_path": project_path,
        "main_space": main_space,
        "feature_space": feature_space,
        "zzz_dir": zzz_dir
    }


@pytest.fixture
def mock_console_select(monkeypatch):
    """Mock Console.prompt_select to return a predefined value."""
    def _mock_select(responses=None):
        if responses is None:
            responses = []
        
        responses_iter = iter(responses)
        
        def mock_select(message, choices, default=None):
            try:
                return next(responses_iter)
            except StopIteration:
                return choices[0] if choices else default
        
        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_select", mock_select)
        return mock_select
    
    return _mock_select


@pytest.fixture
def mock_console_input(monkeypatch):
    """Mock Console.prompt_input to return predefined values."""
    def _mock_input(responses=None):
        if responses is None:
            responses = []
        
        responses_iter = iter(responses)
        
        def mock_input(message, default=""):
            try:
                return next(responses_iter)
            except StopIteration:
                return default
        
        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_input", mock_input)
        return mock_input
    
    return _mock_input


@pytest.fixture
def mock_console_confirm(monkeypatch):
    """Mock Console.prompt_confirm to return predefined values."""
    def _mock_confirm(responses=None):
        if responses is None:
            responses = []
        
        responses_iter = iter(responses)
        
        def mock_confirm(message, default=True):
            try:
                return next(responses_iter)
            except StopIteration:
                return default
        
        from gitspaces.modules.console import Console
        monkeypatch.setattr(Console, "prompt_confirm", mock_confirm)
        return mock_confirm
    
    return _mock_confirm
