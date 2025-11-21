"""Config command for GitSpaces - view and edit configuration."""

from gitspaces.modules.config import Config
from gitspaces.modules.console import Console


def config_command(args):
    """View or edit configuration values.

    Args:
        args: Parsed command-line arguments containing:
            - key: Optional configuration key
            - value: Optional configuration value
    """
    config = Config.instance()

    # If no key provided, show all configuration
    if not hasattr(args, "key") or not args.key:
        Console.println("GitSpaces Configuration")
        Console.println("=" * 50)
        Console.println(f"Config file: {config.config_file}")
        Console.println("\nSettings:")
        Console.println(f"  project_paths: {config.project_paths}")
        Console.println(f"  default_editor: {config.default_editor}")
        return

    key = args.key

    # If no value provided, show the current value
    if not hasattr(args, "value") or not args.value:
        value = config.get(key)
        if value is not None:
            Console.println(f"{key}: {value}")
        else:
            Console.println(f"✗ Configuration key '{key}' not found")
        return

    # Set the configuration value
    value = args.value

    # Handle special keys
    if key == "project_paths":
        # For project_paths, treat value as a single path to add
        current_paths = config.project_paths
        if value not in current_paths:
            current_paths.append(value)
            config.project_paths = current_paths
            Console.println(f"✓ Added '{value}' to project_paths")
        else:
            Console.println(f"Path '{value}' already in project_paths")
    else:
        config.set(key, value)
        Console.println(f"✓ Set {key} = {value}")

    # Save configuration
    config.save()
