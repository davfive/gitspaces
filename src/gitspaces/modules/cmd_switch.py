"""Switch command for GitSpaces - switch between spaces."""

import os
from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project


def switch_command(args):
    """Switch to a different space.
    
    Args:
        args: Parsed command-line arguments containing:
            - space: Optional space name to switch to
    """
    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))
    
    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        Console.println("Run 'gitspaces create <url>' to create a new project")
        return
    
    # List available spaces
    spaces = project.list_spaces()
    
    if not spaces:
        Console.println("✗ No spaces found in project")
        return
    
    # If space name provided, use it
    if hasattr(args, 'space') and args.space:
        target_space = args.space
        if target_space not in spaces:
            Console.println(f"✗ Space '{target_space}' not found")
            Console.println(f"Available spaces: {', '.join(spaces)}")
            return
    else:
        # Interactive selection
        Console.println(f"Project: {project.name}")
        Console.println(f"Available spaces:")
        target_space = Console.prompt_select(
            "Select a space:",
            choices=spaces
        )
    
    # Construct the target path
    if target_space.startswith('.zzz/'):
        Console.println(f"✗ Cannot switch to sleeping space '{target_space}'")
        Console.println("Wake it first with 'gitspaces sleep' (which can wake sleeping spaces)")
        return
    
    target_path = project.path / target_space
    
    # Change directory
    try:
        os.chdir(target_path)
        Console.println(f"✓ Switched to space: {target_space}")
        Console.println(f"  Path: {target_path}")
    except Exception as e:
        Console.println(f"✗ Error switching to space: {e}")
        raise
