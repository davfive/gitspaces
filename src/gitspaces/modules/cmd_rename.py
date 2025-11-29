"""Rename command for GitSpaces - rename spaces."""

from pathlib import Path
from typing import Optional
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space
from gitspaces.modules.path import write_shell_target
from gitspaces.modules import runshell


def _get_current_space_name(project: Project) -> Optional[str]:
    """Get the name of the current space if we're in one.

    Args:
        project: The current project.

    Returns:
        The space name if in a space directory, None otherwise.
    """
    cwd = Path.cwd()
    spaces = project.list_spaces()

    for space_name in spaces:
        space_path = project.path / space_name

        if cwd == space_path or (
            cwd.is_relative_to(space_path) and not cwd.is_relative_to(project.zzz_dir)
        ):
            return space_name

    return None


def rename_command(args):
    """Rename a space.

    Args:
        args: Parsed command-line arguments containing:
            - old_name: Current space name (optional - uses current clone if not provided)
            - new_name: New space name
    """
    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))

    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        return

    # Handle the case where only new_name is provided
    old_name = getattr(args, "old_name", None)
    new_name = getattr(args, "new_name", None)

    # If new_name is not set but old_name is, treat old_name as new_name
    # (this happens when only one arg is passed and it goes to old_name)
    if old_name and not new_name:
        # Detect current space
        current_space = _get_current_space_name(project)
        if current_space:
            new_name = old_name
            old_name = current_space
        else:
            Console.println("✗ Not in a space directory. Specify both old_name and new_name.")
            return

    if not old_name or not new_name:
        Console.println("✗ Both old_name and new_name are required")
        return

    # Check if old space exists
    spaces = project.list_spaces()
    if old_name not in spaces:
        Console.println(f"✗ Space '{old_name}' not found")
        Console.println(f"Available spaces: {', '.join(spaces)}")
        return

    # Check if new name already exists
    if new_name in spaces:
        Console.println(f"✗ Space '{new_name}' already exists")
        return

    # Rename the space
    space_path = project.path / old_name

    space = Space(project, str(space_path))

    try:
        renamed_space = space.rename(new_name)

        # Write shell target for cd to new path
        write_shell_target(renamed_space.path)

        Console.println(f"✓ Renamed space '{old_name}' to '{new_name}'")
        Console.println(f"  New path: {renamed_space.path}")

        # Change directory to the renamed space
        runshell.fs.chdir(str(renamed_space.path))
    except Exception as e:
        Console.println(f"✗ Error renaming space: {e}")
        raise
