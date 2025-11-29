"""Clone command for GitSpaces - clone git repositories as GitSpaces projects."""

import os
from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space
from gitspaces.modules.path import write_shell_target
from gitspaces.modules import runshell


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
        project_paths = config.project_paths

        if len(project_paths) == 1:
            # Use the only configured project path
            target_dir = Path(project_paths[0]).expanduser().resolve()
        else:
            # Prompt user to select from configured project paths
            Console.println("Select target directory for the project:")
            selected_path = Console.prompt_select(
                "Choose a project directory:", choices=project_paths
            )
            target_dir = Path(selected_path).expanduser().resolve()
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

        # After creation, wake one sleeper and cd into it
        sleeping_spaces = [s for s in project.list_spaces() if s.startswith(".zzz/")]

        if sleeping_spaces:
            Console.println("\nLet's set up your first working space!")

            # Get name for the first space
            default_name = "main"
            new_name = Console.prompt_input(
                "Enter a name for your first space:",
                default=default_name,
            )

            if new_name:
                # Wake the first sleeper
                sleeper_name = sleeping_spaces[0]
                sleeper_path = project.path / sleeper_name
                space = Space(project, str(sleeper_path))

                try:
                    woken_space = space.wake(new_name)

                    # Write shell target for cd
                    write_shell_target(woken_space.path)

                    Console.println(f"\n✓ Created space '{new_name}'")
                    Console.println(f"  Path: {woken_space.path}")

                    # Change directory
                    runshell.fs.chdir(str(woken_space.path))
                except Exception as e:
                    Console.println(f"✗ Error creating space: {e}")
                    Console.println("Use 'gitspaces switch' to activate a space.")
            else:
                Console.println("\nUse 'gitspaces switch' to activate a space.")
        else:
            Console.println("\nUse 'gitspaces switch' to activate a space.")

    except Exception as e:
        Console.println(f"\n✗ Error creating project: {e}")
        raise
