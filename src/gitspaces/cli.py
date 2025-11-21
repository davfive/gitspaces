"""GitSpaces CLI - Command-line interface for gitspaces."""

import sys
import argparse
from gitspaces import __version__
from gitspaces.modules.config import Config, init_config, run_user_environment_checks
from gitspaces.modules.console import Console


def create_parser():
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="gitspaces",
        description="GitSpaces - Concurrent development manager for git projects",
        epilog='Use "gitspaces <command> --help" for more information about a command.',
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Add additional debugging information"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import and register commands
    from gitspaces.modules import (
        cmd_setup,
        cmd_clone,
        cmd_switch,
        cmd_sleep,
        cmd_rename,
        cmd_code,
        cmd_config,
        cmd_extend,
    )

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup GitSpaces configuration")
    setup_parser.set_defaults(func=cmd_setup.setup_command)

    # Clone command
    clone_parser = subparsers.add_parser(
        "clone", help="Clone a git repository as a GitSpaces project"
    )
    clone_parser.add_argument("url", help="Git repository URL")
    clone_parser.add_argument(
        "-n", "--num-spaces", type=int, default=3, help="Number of spaces to create (default: 3)"
    )
    clone_parser.add_argument("-d", "--directory", help="Directory where project will be created")
    clone_parser.set_defaults(func=cmd_clone.clone_command)

    # Switch command
    switch_parser = subparsers.add_parser("switch", help="Switch to a different space")
    switch_parser.add_argument("space", nargs="?", help="Space name to switch to")
    switch_parser.set_defaults(func=cmd_switch.switch_command)

    # Sleep command
    sleep_parser = subparsers.add_parser(
        "sleep", help="Put a space to sleep and optionally wake another"
    )
    sleep_parser.add_argument("space", nargs="?", help="Space to put to sleep")
    sleep_parser.set_defaults(func=cmd_sleep.sleep_command)

    # Rename command
    rename_parser = subparsers.add_parser("rename", help="Rename a space")
    rename_parser.add_argument("old_name", help="Current space name")
    rename_parser.add_argument("new_name", help="New space name")
    rename_parser.set_defaults(func=cmd_rename.rename_command)

    # Code command
    code_parser = subparsers.add_parser("code", help="Open space in VS Code")
    code_parser.add_argument("space", nargs="?", help="Space to open")
    code_parser.set_defaults(func=cmd_code.code_command)

    # Config command
    config_parser = subparsers.add_parser("config", help="View or edit configuration")
    config_parser.add_argument("key", nargs="?", help="Configuration key")
    config_parser.add_argument("value", nargs="?", help="Configuration value")
    config_parser.set_defaults(func=cmd_config.config_command)

    # Extend command
    extend_parser = subparsers.add_parser("extend", help="Add more clone spaces to the project")
    extend_parser.add_argument(
        "-n",
        "--num-spaces",
        type=int,
        default=1,
        help="Number of additional spaces to create (default: 1)",
    )
    extend_parser.add_argument(
        "space", nargs="?", help="Space to clone from (default: current or first active)"
    )
    extend_parser.set_defaults(func=cmd_extend.extend_command)

    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Show debug info if requested
    if args.debug:
        Console.println(f"Args: {sys.argv}")

    # Initialize configuration
    try:
        init_config()
        if not run_user_environment_checks():
            sys.exit(1)
    except Exception as e:
        Console.println(f"Error initializing GitSpaces configuration: {e}")
        Console.println("Try running 'gitspaces setup' to configure GitSpaces.")
        sys.exit(1)

    # If no command is provided, default to switch
    if args.command is None:
        from gitspaces.modules import cmd_switch

        args.func = cmd_switch.switch_command

    # Execute the command
    try:
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        Console.println("\nAborted by user")
        sys.exit(1)
    except Exception as e:
        if str(e) != "user aborted":
            Console.println(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
