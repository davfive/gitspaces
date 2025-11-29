"""Code command for GitSpaces - open spaces in editor."""

import json
from pathlib import Path
from typing import Optional
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
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
        if space_name.startswith(".zzz/"):
            continue  # Skip sleeping spaces

        space_path = project.path / space_name

        if cwd == space_path or (
            cwd.is_relative_to(space_path) and not cwd.is_relative_to(project.zzz_dir)
        ):
            return space_name

    return None


def _ensure_workspace_file(project: Project, space_name: str) -> Path:
    """Ensure a .code-workspace file exists for the space.

    Creates the workspace file if it doesn't exist.

    Args:
        project: The project containing the space.
        space_name: The name of the space.

    Returns:
        Path to the workspace file.
    """
    # Create .code-workspace directory if needed
    ws_dir = project.path / ".code-workspace"
    ws_dir.mkdir(parents=True, exist_ok=True)

    # Workspace file name: project~space.code-workspace
    ws_filename = f"{project.name}~{space_name}.code-workspace"
    ws_path = ws_dir / ws_filename

    if not ws_path.exists():
        # Create workspace file
        space_path = project.path / space_name

        workspace_config = {
            "folders": [{"path": str(space_path)}],
            "settings": {},
        }

        ws_path.write_text(json.dumps(workspace_config, indent=2))

    return ws_path


def code_command(args):
    """Open a space in the configured editor (default: VS Code).

    Args:
        args: Parsed command-line arguments containing:
            - space: Optional space to open
    """
    config = Config.instance()
    editor = config.default_editor

    # Find the current project
    cwd = Path.cwd()
    project = Project.find_project(str(cwd))

    if not project:
        Console.println("✗ Not in a GitSpaces project directory")
        return

    # Determine which space to open
    if hasattr(args, "space") and args.space:
        space_name = args.space
    else:
        # Check if we're in a space directory - use it automatically
        current_space = _get_current_space_name(project)

        if current_space:
            space_name = current_space
        else:
            # List available active spaces for selection
            spaces = project.list_spaces()
            active_spaces = [s for s in spaces if not s.startswith(".zzz/")]

            if not active_spaces:
                Console.println("✗ No active spaces available")
                return

            space_name = Console.prompt_select("Select a space to open:", choices=active_spaces)

    # Construct the space path
    space_path = project.path / space_name

    if not space_path.exists():
        Console.println(f"✗ Space '{space_name}' not found")
        return

    # Get or create workspace file
    workspace_file = _ensure_workspace_file(project, space_name)

    # Open workspace file in editor
    try:
        Console.println(f"Opening '{space_name}' in {editor}...")
        runshell.subprocess.run([editor, str(workspace_file)], check=True)
        Console.println(f"✓ Opened workspace in {editor}")
    except FileNotFoundError:
        Console.println(f"✗ Editor '{editor}' not found")
        Console.println("Update your editor with: gitspaces config default_editor <editor>")
    except Exception as e:
        Console.println(f"✗ Error opening editor: {e}")
        raise
