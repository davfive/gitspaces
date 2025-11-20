"""Sleep command for GitSpaces - put spaces to sleep and wake them."""

import os
from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space


def sleep_command(args):
    """Put a space to sleep and optionally wake another.
    
    Args:
        args: Parsed command-line arguments containing:
            - space: Optional space to put to sleep
    """
    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))
    
    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        return
    
    # List available spaces
    spaces = project.list_spaces()
    active_spaces = [s for s in spaces if not s.startswith('.zzz/')]
    sleeping_spaces = [s for s in spaces if s.startswith('.zzz/')]
    
    # Determine which space to sleep
    if hasattr(args, 'space') and args.space:
        space_to_sleep = args.space
    else:
        if not active_spaces:
            Console.println("✗ No active spaces to put to sleep")
            return
        
        Console.println("Active spaces:")
        space_to_sleep = Console.prompt_select(
            "Select a space to put to sleep:",
            choices=active_spaces
        )
    
    if space_to_sleep not in active_spaces:
        Console.println(f"✗ Space '{space_to_sleep}' not found or already sleeping")
        return
    
    # Sleep the space
    space_path = project.path / space_to_sleep
    space = Space(project, str(space_path))
    
    try:
        sleeping_space = space.sleep()
        Console.println(f"✓ Space '{space_to_sleep}' is now sleeping")
    except Exception as e:
        Console.println(f"✗ Error putting space to sleep: {e}")
        return
    
    # Ask if user wants to wake a sleeping space
    if sleeping_spaces:
        wake_another = Console.prompt_confirm(
            "Would you like to wake a sleeping space?",
            default=True
        )
        
        if wake_another:
            space_to_wake = Console.prompt_select(
                "Select a sleeping space to wake:",
                choices=sleeping_spaces
            )
            
            # Get new name for the space
            new_name = Console.prompt_input(
                "Enter a name for the woken space:",
                default=space_to_wake.split('/')[-1].replace('zzz-', '')
            )
            
            sleeping_space_path = project.path / space_to_wake
            sleeping_space_obj = Space(project, str(sleeping_space_path))
            
            try:
                woken_space = sleeping_space_obj.wake(new_name)
                Console.println(f"✓ Space '{space_to_wake}' is now awake as '{new_name}'")
                Console.println(f"  Path: {woken_space.path}")
            except Exception as e:
                Console.println(f"✗ Error waking space: {e}")
