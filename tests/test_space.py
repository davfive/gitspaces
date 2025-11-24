"""Tests for space module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from gitspaces.modules.space import Space
from gitspaces.modules.errors import SpaceError


@patch("gitspaces.modules.space.runshell")
def test_space_init(mock_runshell):
    """Test Space initialization."""
    mock_project = Mock()
    space = Space(mock_project, "/test/project/main")

    assert space.project == mock_project
    assert space.path == Path("/test/project/main")
    assert space.name == "main"


@patch("gitspaces.modules.space.runshell")
def test_space_repo_property(mock_runshell):
    """Test Space repo property."""
    mock_project = Mock()
    mock_repo = Mock()
    mock_runshell.git.get_repo.return_value = mock_repo

    space = Space(mock_project, "/test/project/main")
    repo = space.repo

    assert repo == mock_repo
    mock_runshell.git.get_repo.assert_called_once()

    # Test caching
    repo2 = space.repo
    assert repo2 == mock_repo
    assert mock_runshell.git.get_repo.call_count == 1


@patch("gitspaces.modules.space.runshell")
def test_create_space_from_url(mock_runshell):
    """Test creating space from URL."""
    mock_project = Mock()

    with patch("gitspaces.modules.space.Path.exists", return_value=False):
        space = Space.create_space_from_url(
            mock_project, "https://github.com/test/repo.git", "/test/project/main"
        )

    mock_runshell.git.clone.assert_called_once_with(
        "https://github.com/test/repo.git", "/test/project/main"
    )
    assert space.name == "main"


@patch("gitspaces.modules.space.runshell")
def test_create_space_from_url_exists(mock_runshell):
    """Test creating space when path already exists."""
    mock_project = Mock()

    with patch("gitspaces.modules.space.Path.exists", return_value=True):
        with pytest.raises(SpaceError, match="already exists"):
            Space.create_space_from_url(
                mock_project, "https://github.com/test/repo.git", "/test/project/main"
            )


@patch("gitspaces.modules.space.runshell")
def test_space_duplicate(mock_runshell):
    """Test duplicating a space."""
    mock_project = Mock()
    mock_project._get_empty_sleeper_path.return_value = "/test/project/.zzz/sleep1"

    space = Space(mock_project, "/test/project/main")
    new_space = space.duplicate()

    mock_runshell.fs.copy_tree.assert_called_once_with(
        "/test/project/main", "/test/project/.zzz/sleep1", symlinks=True
    )
    assert new_space.name == "sleep1"


@patch("gitspaces.modules.space.runshell")
def test_space_duplicate_error(mock_runshell):
    """Test duplicate error handling."""
    mock_project = Mock()
    mock_project._get_empty_sleeper_path.return_value = "/test/project/.zzz/sleep1"
    mock_runshell.fs.copy_tree.side_effect = Exception("Copy failed")

    space = Space(mock_project, "/test/project/main")

    with pytest.raises(SpaceError, match="Failed to duplicate"):
        space.duplicate()


@patch("gitspaces.modules.space.runshell")
def test_space_wake(mock_runshell):
    """Test waking a sleeping space."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/.zzz/sleep1")

    with patch.object(Path, "exists", return_value=False):
        woken_space = space.wake("feature")

    mock_runshell.fs.move.assert_called_once()
    assert "feature" in str(mock_runshell.fs.move.call_args[0][1])


@patch("gitspaces.modules.space.runshell")
def test_space_wake_not_sleeping(mock_runshell):
    """Test waking a space that's not sleeping."""
    mock_project = Mock()
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/main")

    with pytest.raises(SpaceError, match="not sleeping"):
        space.wake()


@patch("gitspaces.modules.space.runshell")
def test_space_wake_exists(mock_runshell):
    """Test waking to existing path."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/.zzz/sleep1")

    with patch.object(Path, "exists", return_value=True):
        with pytest.raises(SpaceError, match="already exists"):
            space.wake("main")


@patch("gitspaces.modules.space.runshell")
def test_space_wake_auto_name(mock_runshell):
    """Test waking with automatic naming."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")
    mock_project.zzz_dir = Path("/test/project/.zzz")

    mock_repo = Mock()
    mock_runshell.git.get_active_branch.return_value = "develop"

    space = Space(mock_project, "/test/project/.zzz/sleep1")
    space._repo = mock_repo

    with patch.object(Path, "exists", return_value=False):
        woken_space = space.wake()

    mock_runshell.fs.move.assert_called_once()


@patch("gitspaces.modules.space.runshell")
def test_space_sleep(mock_runshell):
    """Test putting space to sleep."""
    mock_project = Mock()
    mock_project.zzz_dir = Path("/test/project/.zzz")
    mock_project._get_empty_sleeper_path.return_value = "/test/project/.zzz/sleep1"

    space = Space(mock_project, "/test/project/main")
    sleeping_space = space.sleep()

    mock_runshell.fs.move.assert_called_once_with("/test/project/main", "/test/project/.zzz/sleep1")


@patch("gitspaces.modules.space.runshell")
def test_space_sleep_already_sleeping(mock_runshell):
    """Test sleeping space that's already sleeping."""
    mock_project = Mock()
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/.zzz/sleep1")

    with pytest.raises(SpaceError, match="already sleeping"):
        space.sleep()


@patch("gitspaces.modules.space.runshell")
def test_space_rename(mock_runshell):
    """Test renaming a space."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")

    space = Space(mock_project, "/test/project/main")

    with patch.object(Path, "exists", return_value=False):
        renamed_space = space.rename("feature")

    mock_runshell.fs.move.assert_called_once()
    assert "feature" in str(mock_runshell.fs.move.call_args[0][1])


@patch("gitspaces.modules.space.runshell")
def test_space_rename_sleeping(mock_runshell):
    """Test renaming a sleeping space."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/.zzz/sleep1")

    with patch.object(Path, "exists", return_value=False):
        renamed_space = space.rename("sleep2")

    mock_runshell.fs.move.assert_called_once()


@patch("gitspaces.modules.space.runshell")
def test_space_rename_exists(mock_runshell):
    """Test renaming to existing name."""
    mock_project = Mock()
    mock_project.path = Path("/test/project")

    space = Space(mock_project, "/test/project/main")

    with patch.object(Path, "exists", return_value=True):
        with pytest.raises(SpaceError, match="already exists"):
            space.rename("feature")


@patch("gitspaces.modules.space.runshell")
def test_space_get_current_branch(mock_runshell):
    """Test getting current branch."""
    mock_project = Mock()
    mock_repo = Mock()
    mock_runshell.git.get_active_branch.return_value = "main"

    space = Space(mock_project, "/test/project/main")
    space._repo = mock_repo

    branch = space.get_current_branch()
    assert branch == "main"


@patch("gitspaces.modules.space.runshell")
def test_space_get_current_branch_no_repo(mock_runshell):
    """Test getting current branch with no repo."""
    mock_project = Mock()
    mock_runshell.git.get_repo.return_value = None

    space = Space(mock_project, "/test/project/main")

    branch = space.get_current_branch()
    assert branch == "detached"


@patch("gitspaces.modules.space.runshell")
def test_space_is_sleeping_true(mock_runshell):
    """Test is_sleeping returns True."""
    mock_project = Mock()
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/.zzz/sleep1")
    assert space.is_sleeping() is True


@patch("gitspaces.modules.space.runshell")
def test_space_is_sleeping_false(mock_runshell):
    """Test is_sleeping returns False."""
    mock_project = Mock()
    mock_project.zzz_dir = Path("/test/project/.zzz")

    space = Space(mock_project, "/test/project/main")
    assert space.is_sleeping() is False
