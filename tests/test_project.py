"""Tests for project module."""

import pytest
from pathlib import Path
from gitspaces.modules.project import Project
from gitspaces.modules.errors import ProjectError


def test_project_init():
    """Test Project initialization."""
    project = Project("/test/path/myproject")
    
    assert project.path == Path("/test/path/myproject")
    assert project.name == "myproject"
    assert project.dotfile == Path("/test/path/myproject/__GITSPACES_PROJECT__")
    assert project.zzz_dir == Path("/test/path/myproject/.zzz")


def test_extract_project_name():
    """Test project name extraction from URL."""
    # HTTPS URL
    name = Project._extract_project_name("https://github.com/user/repo.git")
    assert name == "repo"
    
    # SSH URL
    name = Project._extract_project_name("git@github.com:user/myrepo.git")
    assert name == "myrepo"
    
    # Without .git
    name = Project._extract_project_name("https://github.com/user/project")
    assert name == "project"


def test_project_exists(tmp_path):
    """Test project existence check."""
    project_path = tmp_path / "testproject"
    project = Project(str(project_path))
    
    # Should not exist initially
    assert not project.exists()
    
    # Create structure
    project.path.mkdir()
    project.dotfile.touch()
    
    # Should exist now
    assert project.exists()


def test_find_project(tmp_path):
    """Test finding a project by searching upward."""
    # Create project structure
    project_path = tmp_path / "myproject"
    project_path.mkdir()
    (project_path / "__GITSPACES_PROJECT__").touch()
    
    # Create subdirectory
    subdir = project_path / "space1" / "src"
    subdir.mkdir(parents=True)
    
    # Find from subdirectory
    found = Project.find_project(str(subdir))
    
    assert found is not None
    assert found.path == project_path
    assert found.name == "myproject"


def test_find_project_not_found(tmp_path):
    """Test finding project when not in a project."""
    # No project marker
    result = Project.find_project(str(tmp_path))
    assert result is None


def test_list_spaces(tmp_path):
    """Test listing spaces in a project."""
    project_path = tmp_path / "testproject"
    project = Project(str(project_path))
    
    # Create project structure
    project_path.mkdir()
    project.dotfile.touch()
    project.zzz_dir.mkdir()
    
    # Create some spaces
    (project_path / "space1").mkdir()
    (project_path / "space2").mkdir()
    (project.zzz_dir / "zzz-0").mkdir()
    (project.zzz_dir / "zzz-1").mkdir()
    
    spaces = project.list_spaces()
    
    assert "space1" in spaces
    assert "space2" in spaces
    assert ".zzz/zzz-0" in spaces
    assert ".zzz/zzz-1" in spaces
    assert len(spaces) == 4
