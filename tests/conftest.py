"""Pytest configuration and fixtures for GitSpaces tests."""

from __future__ import annotations

import gc
import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock
import pytest
import yaml
from git import Repo


def _robust_rmtree(path: Path, retries: int = 5, delay: float = 0.5):
    """Remove directory tree with retries for Windows file locking issues.

    On Windows, Git processes may hold file handles open briefly after repo.close().
    This function retries deletion with exponential backoff.
    """
    max_delay = 2.0  # Cap maximum delay at 2 seconds
    for attempt in range(retries):
        try:
            # Force garbage collection to release any Python-held handles
            gc.collect()
            shutil.rmtree(path, ignore_errors=False)
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(min(delay * (2**attempt), max_delay))
            else:
                # Final attempt: use ignore_errors to clean up what we can
                shutil.rmtree(path, ignore_errors=True)
        except FileNotFoundError:
            return  # Already deleted


def _close_git_repos_in_directory(directory: Path):
    """Close any Git repository objects to release file handles.

    This is important on Windows where file handles prevent deletion.
    This function uses GitPython's global cache clearing mechanism
    for efficiency rather than creating new Repo objects.
    """
    if not directory.exists():
        return

    # Clear GitPython's global Git command cache which holds file handles
    try:
        from git import Git

        Git.clear_cache()
    except Exception:
        pass  # Ignore errors - we're just trying to release handles

    # Also try garbage collection to release any remaining handles
    gc.collect()


@pytest.fixture
def temp_home(monkeypatch):
    """Create a temporary home directory for testing."""
    # Create temp directory manually for better control over cleanup
    temp_dir = tempfile.mkdtemp()
    temp_home_path = Path(temp_dir).resolve() / "home"
    temp_home_path.mkdir()

    # Set HOME environment variable
    monkeypatch.setenv("HOME", str(temp_home_path))
    monkeypatch.setenv("USERPROFILE", str(temp_home_path))  # For Windows

    yield temp_home_path

    # Cleanup with proper handling for Windows file locking
    _close_git_repos_in_directory(Path(temp_dir))
    _robust_rmtree(Path(temp_dir))


@pytest.fixture
def temp_git_repo(temp_home):
    """Create a temporary git repository for testing."""
    repo_path = (temp_home / "test-repo").resolve()
    repo_path.mkdir()

    # Initialize git repo with resolved path
    repo = Repo.init(str(repo_path))

    # Create initial commit using resolved path
    readme = repo_path / "README.md"
    readme.write_text("# Test Repository\n")
    # Use relative path for git operations to avoid symlink issues
    # Change to repo directory to ensure relative paths work correctly
    original_dir = os.getcwd()
    try:
        os.chdir(str(repo_path))
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")
    finally:
        os.chdir(original_dir)
        # Close repo to release file handles (important for Windows)
        repo.close()

    return repo_path


@pytest.fixture
def gitspaces_config(temp_home, monkeypatch):
    """Create a GitSpaces configuration file."""
    config_dir = temp_home / ".gitspaces"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.yml"
    projects_dir = temp_home / "code" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    config_data = {"project_paths": [str(projects_dir)], "default_editor": "code"}

    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    # Reset Config singleton
    from gitspaces.modules.config import Config

    Config._instance = None
    Config._config_dir = None
    Config._config_file = None
    Config._data = {}

    yield {"config_dir": config_dir, "config_file": config_file, "projects_dir": projects_dir}


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
    repo = Repo.init(str(main_space))
    readme = main_space / "README.md"
    readme.write_text("# Test Project\n")
    # Use relative path for git operations to avoid path issues on Windows
    # Change to repo directory to ensure relative paths work correctly
    original_dir = os.getcwd()
    try:
        os.chdir(str(main_space))
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")
    finally:
        os.chdir(original_dir)
        # Close repo to release file handles (important for Windows)
        repo.close()
        if hasattr(repo, "git"):
            repo.git.clear_cache()

    # Create feature space
    feature_space = project_path / "feature"
    shutil.copytree(main_space, feature_space)

    project = Project(str(project_path))

    yield {
        "project": project,
        "project_path": project_path,
        "main_space": main_space,
        "feature_space": feature_space,
        "zzz_dir": zzz_dir,
    }

    # Cleanup: Close all git repos in the project directory to release file handles
    # This is handled by temp_home fixture cleanup, but we explicitly close here
    # to ensure handles are released before any other cleanup happens
    _close_git_repos_in_directory(project_path)


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


@pytest.fixture
def bare_git_repo(temp_home):
    """Create a bare git repository suitable for cloning.

    This is used for testing clone operations without network access.
    """
    repo_path = (temp_home / "bare-repo.git").resolve()

    # Create a regular repo first, then make a bare clone
    source_path = (temp_home / "source-repo").resolve()
    source_path.mkdir()

    # Initialize source repo
    repo = Repo.init(str(source_path))
    readme = source_path / "README.md"
    readme.write_text("# Test Repository\n")

    original_dir = os.getcwd()
    try:
        os.chdir(str(source_path))
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        # Create bare clone
        Repo.clone_from(str(source_path), str(repo_path), bare=True)
    finally:
        os.chdir(original_dir)
        repo.close()

    yield repo_path

    # Cleanup
    _close_git_repos_in_directory(repo_path)


@pytest.fixture
def gitspaces_project_with_sleepers(temp_home, gitspaces_config, temp_git_repo):
    """Create a GitSpaces project with both active and sleeping spaces."""
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
    repo = Repo.init(str(main_space))
    readme = main_space / "README.md"
    readme.write_text("# Test Project\n")

    original_dir = os.getcwd()
    try:
        os.chdir(str(main_space))
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")
    finally:
        os.chdir(original_dir)
        repo.close()
        if hasattr(repo, "git"):
            repo.git.clear_cache()

    # Create sleeping spaces
    sleeper1 = zzz_dir / "zzz-0"
    sleeper2 = zzz_dir / "zzz-1"
    shutil.copytree(main_space, sleeper1)
    shutil.copytree(main_space, sleeper2)

    project = Project(str(project_path))

    yield {
        "project": project,
        "project_path": project_path,
        "main_space": main_space,
        "zzz_dir": zzz_dir,
        "sleeper1": sleeper1,
        "sleeper2": sleeper2,
    }

    _close_git_repos_in_directory(project_path)


@pytest.fixture
def multiple_projects(temp_home, gitspaces_config):
    """Create multiple GitSpaces projects for testing project listing."""
    from gitspaces.modules.project import Project

    projects_dir = gitspaces_config["projects_dir"]
    projects = []

    for i, name in enumerate(["project-alpha", "project-beta", "project-gamma"]):
        project_path = projects_dir / name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create project marker file
        dotfile = project_path / Project.DOTFILE
        dotfile.touch()

        # Create .zzz directory
        zzz_dir = project_path / Project.ZZZ_DIR
        zzz_dir.mkdir(exist_ok=True)

        # Create a space
        space = project_path / "main"
        space.mkdir(exist_ok=True)

        # Initialize as git repo
        repo = Repo.init(str(space))
        readme = space / "README.md"
        readme.write_text(f"# {name}\n")

        original_dir = os.getcwd()
        try:
            os.chdir(str(space))
            repo.index.add(["README.md"])
            repo.index.commit("Initial commit")
        finally:
            os.chdir(original_dir)
            repo.close()

        projects.append({
            "name": name,
            "path": project_path,
            "space": space,
            "zzz_dir": zzz_dir,
        })

    yield {
        "projects_dir": projects_dir,
        "projects": projects,
    }

    for proj in projects:
        _close_git_repos_in_directory(proj["path"])


@pytest.fixture
def shell_pid_file(temp_home):
    """Fixture to check and cleanup shell PID files after tests."""
    gitspaces_dir = temp_home / ".gitspaces"
    gitspaces_dir.mkdir(parents=True, exist_ok=True)

    pid = os.getpid()
    pid_file = gitspaces_dir / f"pid-{pid}"

    yield {
        "dir": gitspaces_dir,
        "pid": pid,
        "file": pid_file,
    }

    # Cleanup the PID file if it exists
    if pid_file.exists():
        pid_file.unlink()
