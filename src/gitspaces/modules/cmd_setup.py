"""Setup command for GitSpaces initial configuration."""

from pathlib import Path
from gitspaces.modules.config import Config
from gitspaces.modules.console import Console
from gitspaces.modules.path import ensure_dir


def setup_command(args):
    """Setup GitSpaces configuration."""
    Console.println("GitSpaces Setup")
    Console.println("=" * 50)

    # Run the setup process
    result = run_setup()

    if result:
        Console.println("\n✓ Setup complete!")
        Console.println("You can now use 'gitspaces' or 'gs' commands.")
    else:
        Console.println("\n✗ Setup incomplete. Please try again.")


def run_setup() -> bool:
    """Run the interactive setup process.

    Returns:
        True if setup was successful, False otherwise.
    """
    config = Config.instance()

    Console.println("\n--- Step 1: Configure Project Paths ---")
    Console.println("Where do you keep your git projects?")

    # Get project paths
    paths = []
    while True:
        path = Console.prompt_input(
            "Enter a project directory path (or press Enter to finish):", default=""
        )

        if not path:
            if paths:
                break
            Console.println("At least one project path is required.")
            continue

        # Expand and validate path
        expanded_path = Path(path).expanduser().resolve()
        if not expanded_path.exists():
            create = Console.prompt_confirm(
                f"Directory {expanded_path} does not exist. Create it?", default=True
            )
            if create:
                ensure_dir(expanded_path)
                paths.append(str(expanded_path))
            else:
                continue
        else:
            paths.append(str(expanded_path))

    config.project_paths = paths

    Console.println("\n--- Step 2: Configure Default Editor ---")
    editor = Console.prompt_input(
        "Enter your preferred editor command (e.g., 'code', 'vim'):", default="code"
    )
    config.default_editor = editor

    # Save configuration
    config.save()

    return True
