"""Rename command for GitSpaces - rename spaces."""

from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space


def rename_command(args):
    """Rename a space.
    
    Args:
        args: Parsed command-line arguments containing:
            - old_name: Current space name
            - new_name: New space name
    """
    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))
    
    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        return
    
    old_name = args.old_name
    new_name = args.new_name
    
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
    if old_name.startswith('.zzz/'):
        space_path = project.path / old_name
    else:
        space_path = project.path / old_name
    
    space = Space(project, str(space_path))
    
    try:
        renamed_space = space.rename(new_name)
        Console.println(f"✓ Renamed space '{old_name}' to '{new_name}'")
        Console.println(f"  New path: {renamed_space.path}")
    except Exception as e:
        Console.println(f"✗ Error renaming space: {e}")
        raise
