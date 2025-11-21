"""Code command for GitSpaces - open spaces in editor."""

from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.project import Project
from gitspaces.modules import runshell


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
        # List available active spaces
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

    # Open in editor
    try:
        Console.println(f"Opening '{space_name}' in {editor}...")
        runshell.subprocess.run([editor, str(space_path)], check=True)
        Console.println(f"✓ Opened space in {editor}")
    except FileNotFoundError:
        Console.println(f"✗ Editor '{editor}' not found")
        Console.println("Update your editor with: gitspaces config default_editor <editor>")
    except Exception as e:
        Console.println(f"✗ Error opening editor: {e}")
        raise
