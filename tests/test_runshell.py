"""Tests for runshell module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from gitspaces.modules import runshell
from gitspaces.modules.errors import GitSpacesError


def test_subprocess_run():
    """Test subprocess.run wrapper."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)
        result = runshell.subprocess.run(["echo", "test"])
        mock_run.assert_called_once_with(["echo", "test"])


def test_git_clone_success():
    """Test git clone success."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        runshell.git.clone("https://github.com/test/repo.git", "/tmp/test")
        mock_repo.clone_from.assert_called_once_with(
            "https://github.com/test/repo.git", "/tmp/test"
        )


def test_git_clone_failure():
    """Test git clone failure."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        mock_repo.clone_from.side_effect = Exception("Clone failed")
        with pytest.raises(GitSpacesError):
            runshell.git.clone("https://github.com/test/repo.git", "/tmp/test")


def test_git_get_repo_exists():
    """Test get_repo for existing path."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        with patch("gitspaces.modules.runshell.Path.exists", return_value=True):
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance

            result = runshell.git.get_repo("/test/path")

            assert result == mock_repo_instance


def test_git_get_repo_not_exists():
    """Test get_repo for non-existing path."""
    with patch("gitspaces.modules.runshell.Path.exists", return_value=False):
        result = runshell.git.get_repo("/nonexistent/path")
        assert result is None


def test_git_get_repo_invalid():
    """Test get_repo for invalid repo."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        with patch("gitspaces.modules.runshell.Path.exists", return_value=True):
            mock_repo.side_effect = Exception("Invalid repo")
            result = runshell.git.get_repo("/test/path")
            assert result is None


def test_git_get_active_branch():
    """Test get active branch."""
    mock_repo = Mock()
    mock_repo.active_branch.name = "main"

    result = runshell.git.get_active_branch(mock_repo)
    assert result == "main"


def test_git_get_active_branch_detached():
    """Test get active branch when detached."""
    mock_repo = Mock()
    type(mock_repo).active_branch = property(
        lambda self: (_ for _ in ()).throw(Exception("Detached HEAD"))
    )

    result = runshell.git.get_active_branch(mock_repo)
    assert result == "detached"


def test_git_is_valid_repo_true():
    """Test is_valid_repo returns True."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        result = runshell.git.is_valid_repo("/test/path")
        assert result is True


def test_git_is_valid_repo_false():
    """Test is_valid_repo returns False."""
    with patch("gitspaces.modules.runshell.Repo") as mock_repo:
        mock_repo.side_effect = Exception("Invalid repo")
        result = runshell.git.is_valid_repo("/test/path")
        assert result is False


def test_fs_move_not_inside_src(tmp_path):
    """Test fs.move when not inside the source directory."""
    # Create source directory
    src_dir = tmp_path / "source"
    src_dir.mkdir()
    (src_dir / "file.txt").write_text("test")

    dst_dir = tmp_path / "destination"

    # Move from outside the source directory
    runshell.fs.move(src_dir, dst_dir)

    # Verify the move happened
    assert not src_dir.exists()
    assert dst_dir.exists()
    assert (dst_dir / "file.txt").exists()


def test_fs_move_inside_src_directory(tmp_path, monkeypatch):
    """Test fs.move when current directory is inside the source directory."""
    # Create source directory with a subdirectory
    src_dir = tmp_path / "source"
    src_subdir = src_dir / "subdir"
    src_subdir.mkdir(parents=True)
    (src_subdir / "file.txt").write_text("test")

    dst_dir = tmp_path / "destination"

    # Change into the subdirectory
    monkeypatch.chdir(src_subdir)

    # Move the source directory
    runshell.fs.move(src_dir, dst_dir)

    # Verify the move happened
    assert not src_dir.exists()
    assert dst_dir.exists()
    assert (dst_dir / "subdir" / "file.txt").exists()

    # Verify we're now in the new location
    assert Path.cwd() == dst_dir / "subdir"


def test_fs_copy_tree():
    """Test fs.copy_tree."""
    with patch("gitspaces.modules.runshell.shutil.copytree") as mock_copytree:
        runshell.fs.copy_tree("/src", "/dst", symlinks=True)
        mock_copytree.assert_called_once_with("/src", "/dst", symlinks=True)


def test_fs_copy_tree_no_symlinks():
    """Test fs.copy_tree without symlinks."""
    with patch("gitspaces.modules.runshell.shutil.copytree") as mock_copytree:
        runshell.fs.copy_tree("/src", "/dst", symlinks=False)
        mock_copytree.assert_called_once_with("/src", "/dst", symlinks=False)


def test_fs_chdir():
    """Test fs.chdir."""
    with patch("gitspaces.modules.runshell.os.chdir") as mock_chdir:
        runshell.fs.chdir("/test/path")
        mock_chdir.assert_called_once_with("/test/path")
