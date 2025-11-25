"""Console output and prompting utilities."""

from __future__ import annotations
from typing import Any
from rich.console import Console as RichConsole
import questionary


class Console:
    """Console utilities for output and user prompts."""

    _use_pretty_prompts = True
    _console = RichConsole()

    @classmethod
    def println(cls, message: str, *args: Any) -> None:
        """Print a message to the console.

        Args:
            message: The message format string.
            *args: Arguments for string formatting.
        """
        if args:
            message = message % args
        cls._console.print(message)

    @classmethod
    def set_use_pretty_prompts(cls, use_pretty: bool) -> None   :
        """Set whether to use pretty prompts.

        Args:
            use_pretty: True to use pretty prompts, False for plain.
        """
        cls._use_pretty_prompts = use_pretty

    @classmethod
    def prompt_input(cls, message: str, default: str = "") -> str:
        """Prompt the user for text input.

        Args:
            message: The prompt message.
            default: The default value.

        Returns:
            The user's input.
        """
        return questionary.text(message, default=default).ask() or default

    @classmethod
    def prompt_confirm(cls, message: str, default: bool = True) -> bool:
        """Prompt the user for confirmation.

        Args:
            message: The prompt message.
            default: The default value.

        Returns:
            True if confirmed, False otherwise.
        """
        result = questionary.confirm(message, default=default).ask()
        return result if result is not None else default

    @classmethod
    def prompt_select(cls, message: str, choices: list[str], default: str | None = None) -> str:
        """Prompt the user to select from a list of choices.

        Args:
            message: The prompt message.
            choices: The list of choices.
            default: The default choice.

        Returns:
            The selected choice.
        """
        return str(questionary.select(message, choices=choices, default=default).ask())
