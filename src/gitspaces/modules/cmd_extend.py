"""Extend command for GitSpaces - add more clones to a project."""

from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space


def extend_command(args):
    """Add more clone spaces to the current project.

    Args:
        args: Parsed command-line arguments containing:
            - num_spaces: Number of additional spaces to create
            - space: Optional space to clone from (defaults to current or first active)
    """
    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))

    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        return

    num_spaces = args.num_spaces if hasattr(args, "num_spaces") and args.num_spaces else 1

    # Determine which space to clone from
    spaces = project.list_spaces()
    active_spaces = [s for s in spaces if not s.startswith(".zzz/")]

    if not active_spaces:
        Console.println("✗ No active spaces available to clone from")
        return

    # If space name provided, use it
    if hasattr(args, "space") and args.space:
        source_space_name = args.space
        if source_space_name not in active_spaces:
            Console.println(f"✗ Space '{source_space_name}' not found or is sleeping")
            Console.println(f"Available active spaces: {', '.join(active_spaces)}")
            return
    else:
        # Check if we're currently in a space directory
        current_space = None
        for space_name in active_spaces:
            space_path = project.path / space_name
            if cwd == space_path or cwd.is_relative_to(space_path):
                current_space = space_name
                break

        if current_space:
            source_space_name = current_space
            Console.println(f"Using current space '{source_space_name}' as source")
        else:
            # Use the first active space
            source_space_name = active_spaces[0]
            Console.println(f"Using space '{source_space_name}' as source")

    # Create the source space object
    source_space_path = project.path / source_space_name
    source_space = Space(project, str(source_space_path))

    # Create the additional clones
    Console.println(f"Creating {num_spaces} additional clone(s) from '{source_space_name}'...")

    created_count = 0
    for i in range(num_spaces):
        try:
            new_space = source_space.duplicate()
            created_count += 1
            Console.println(f"  ✓ Created clone {i + 1}/{num_spaces}: {new_space.path.name}")
        except Exception as e:
            Console.println(f"  ✗ Error creating clone {i + 1}: {e}")
            break

    if created_count > 0:
        Console.println(f"\n✓ Successfully created {created_count} additional clone(s)")
        Console.println(f"Total spaces in project: {len(project.list_spaces())}")
        Console.println("\nUse 'gitspaces sleep' to wake and name the new clones")
    else:
        Console.println("\n✗ No clones were created")
