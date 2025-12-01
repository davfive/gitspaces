"""Switch command for GitSpaces - switch between spaces."""

from pathlib import Path
from typing import Optional

from gitspaces.modules import runshell
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.path import write_shell_target
from gitspaces.modules.project import Project
from gitspaces.modules.space import Space


def _find_all_projects() -> list[Project]:
    """Find all GitSpaces projects in configured project paths.

    Returns:
        List of Project instances found.
    """
    config = Config.instance()
    projects = []

    for project_path in config.project_paths:
        path = Path(project_path).expanduser().resolve()
        if not path.exists():
            continue

        # Scan for directories with __GITSPACES_PROJECT__ marker
        for item in path.iterdir():
            if item.is_dir():
                dotfile = item / Project.DOTFILE
                if dotfile.exists():
                    projects.append(Project(str(item)))

    return projects


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
        if space_name.startswith(".zzz/"):
            space_path = project.path / space_name
        else:
            space_path = project.path / space_name

        if cwd == space_path or (
            cwd.is_relative_to(space_path) and not cwd.is_relative_to(project.zzz_dir)
        ):
            return space_name

    return None


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
        # When not in a project, list all projects from config
        projects = _find_all_projects()

        if not projects:
            Console.println("✗ No GitSpaces projects found")
            Console.println("Run 'gitspaces clone <url>' to create a new project")
            return

        # Let user select a project
        project_choices = [p.name for p in projects]
        Console.println("Available projects:")
        selected_name = Console.prompt_select(
            "Select a project:", choices=project_choices
        )

        # Find the selected project
        project = next((p for p in projects if p.name == selected_name), None)
        if not project:
            Console.println(f"✗ Project '{selected_name}' not found")
            return

    # List available spaces
    all_spaces = project.list_spaces()

    if not all_spaces:
        Console.println("✗ No spaces found in project")
        return

    # Separate active and sleeping spaces
    active_spaces = [s for s in all_spaces if not s.startswith(".zzz/")]
    sleeping_spaces = [s for s in all_spaces if s.startswith(".zzz/")]

    # Get current space to filter it out
    current_space = _get_current_space_name(project)

    # Filter out current space from choices
    display_spaces = [s for s in active_spaces if s != current_space]

    # If space name provided, use it
    if hasattr(args, "space") and args.space:
        target_space = args.space

        # Check if it's a sleeping space
        if target_space.startswith(".zzz/"):
            if target_space not in sleeping_spaces:
                Console.println(f"✗ Sleeping space '{target_space}' not found")
                return
            # Wake the sleeper
            _wake_and_switch(project, target_space)
            return

        if target_space not in active_spaces:
            Console.println(f"✗ Space '{target_space}' not found")
            Console.println(f"Available spaces: {', '.join(active_spaces)}")
            return
    else:
        # Build choices for interactive selection
        choices = display_spaces.copy()

        # Add "Wake up" option if there are sleepers
        wake_option = None
        if sleeping_spaces:
            wake_option = f"Wake up ({len(sleeping_spaces)} sleeping)"
            choices.append(wake_option)

        if not choices:
            Console.println("✗ No spaces available to switch to")
            return

        # Interactive selection
        Console.println(f"Project: {project.name}")
        target_space = Console.prompt_select("Select a space:", choices=choices)

        # Handle wake option
        if target_space == wake_option:
            _wake_and_switch(project, None)
            return

    # Construct the target path
    target_path = project.path / target_space

    # Write shell target for cd
    write_shell_target(target_path)

    # Change directory (for when running without shell wrapper)
    try:
        runshell.fs.chdir(str(target_path))
        Console.println(f"✓ Switched to space: {target_space}")
        Console.println(f"  Path: {target_path}")
    except Exception as e:
        Console.println(f"✗ Error switching to space: {e}")
        raise


def _wake_and_switch(project: Project, sleeper_name: Optional[str]):
    """Wake a sleeping space and switch to it.

    Args:
        project: The project containing the sleeper.
        sleeper_name: The sleeper space name (e.g., '.zzz/zzz-0'), or None to prompt.
    """
    sleeping_spaces = [s for s in project.list_spaces() if s.startswith(".zzz/")]

    if not sleeping_spaces:
        Console.println("✗ No sleeping spaces to wake")
        return

    # Select sleeper if not provided
    if sleeper_name is None:
        sleeper_name = Console.prompt_select(
            "Select a sleeping space to wake:", choices=sleeping_spaces
        )

    # Get new name for the space
    default_name = sleeper_name.split("/")[-1].replace("zzz-", "space-")
    new_name = Console.prompt_input(
        "Enter a name for the woken space:",
        default=default_name,
    )

    if not new_name:
        Console.println("✗ A name is required to wake the space")
        return

    # Check if name already exists
    active_spaces = [s for s in project.list_spaces() if not s.startswith(".zzz/")]
    if new_name in active_spaces:
        Console.println(f"✗ Space '{new_name}' already exists")
        return

    # Wake the sleeper
    sleeper_path = project.path / sleeper_name
    space = Space(project, str(sleeper_path))

    try:
        woken_space = space.wake(new_name)

        # Write shell target for cd
        write_shell_target(woken_space.path)

        Console.println(f"✓ Woke space '{sleeper_name}' as '{new_name}'")
        Console.println(f"  Path: {woken_space.path}")

        # Change directory
        runshell.fs.chdir(str(woken_space.path))
    except Exception as e:
        Console.println(f"✗ Error waking space: {e}")
        raise
