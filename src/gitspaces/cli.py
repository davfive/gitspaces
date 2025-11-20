"""GitSpaces CLI - Command-line interface for gitspaces."""

import sys
import click
from gitspaces import __version__
from gitspaces.config.config import Config, init_config, run_user_environment_checks
from gitspaces.console.console import Console
from gitspaces.commands import setup, create, switch, sleep, rename, code, config as config_cmd


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option('--debug', '-d', is_flag=True, hidden=True, help='Add additional debugging information')
@click.option('--plain', '-p', is_flag=True, hidden=True, help='Only use plain prompts')
@click.option('--pretty', '-P', is_flag=True, hidden=True, help='Only use pretty prompts')
@click.option('--wrapid', type=int, default=-1, hidden=True, help='Wrapper ID from calling shell')
@click.pass_context
def cli(ctx, debug, plain, pretty, wrapid):
    """GitSpaces - Concurrent development manager for git projects.
    
    If you're familiar with ClearCase Views, think of GitSpaces as their
    counterpart for Git projects. GitSpaces manages multiple independent
    clones of a project so you can switch between them as you work on
    new features or bugs.
    """
    ctx.ensure_object(dict)
    
    if debug:
        Console.println(f"Args: {sys.argv}")
    
    if plain:
        Console.set_use_pretty_prompts(False)
    
    if pretty:
        Console.set_use_pretty_prompts(True)
    
    # Initialize configuration
    try:
        init_config(wrapid)
        if not run_user_environment_checks():
            sys.exit(1)
    except Exception as e:
        Console.println(f"Error initializing config: {e}")
        sys.exit(1)
    
    # If no subcommand is provided, default to switch
    if ctx.invoked_subcommand is None:
        ctx.invoke(switch.switch)


# Register commands
cli.add_command(setup.setup)
cli.add_command(create.create)
cli.add_command(switch.switch)
cli.add_command(sleep.sleep)
cli.add_command(rename.rename)
cli.add_command(code.code)
cli.add_command(config_cmd.config)


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        if str(e) != "user aborted":
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
