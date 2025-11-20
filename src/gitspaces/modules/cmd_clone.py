"""Clone command for GitSpaces - clone git repositories as GitSpaces projects."""

import os
from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project


def clone_command(args):
    """Clone a git repository as a GitSpaces project.
    
    Args:
        args: Parsed command-line arguments containing:
            - url: Git repository URL
            - num_spaces: Number of spaces to create
            - directory: Optional directory where project will be created
    """
    config = Config.instance()
    url = args.url
    num_spaces = args.num_spaces
    directory = args.directory
    
    # Determine the target directory
    if directory:
        target_dir = Path(directory).expanduser().resolve()
    elif config.project_paths:
        # Use the first configured project path
        target_dir = Path(config.project_paths[0]).expanduser().resolve()
    else:
        # Default to current directory
        target_dir = Path.cwd()
    
    Console.println(f"Creating GitSpaces project from {url}")
    Console.println(f"Location: {target_dir}")
    Console.println(f"Number of spaces: {num_spaces}")
    
    try:
        project = Project.create_project(str(target_dir), url, num_spaces)
        Console.println(f"\n✓ Successfully created project: {project.name}")
        Console.println(f"  Path: {project.path}")
        Console.println(f"\nUse 'gitspaces switch' to activate a space.")
    except Exception as e:
        Console.println(f"\n✗ Error creating project: {e}")
        raise
