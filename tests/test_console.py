"""Tests for console module."""

from unittest.mock import patch

from gitspaces.modules.console import Console


class TestConsole:
    """Test Console class."""

    @patch("rich.console.Console.print")
    def test_println(self, mock_print):
        """Test printing message."""
        Console.println("Test message")

        mock_print.assert_called_once_with("Test message")

    @patch("rich.console.Console.print")
    def test_println_with_format(self, mock_print):
        """Test printing formatted message."""
        Console.println("Test %s", "value")

        mock_print.assert_called_once_with("Test value")

    def test_set_use_pretty_prompts(self):
        """Test setting pretty prompts flag."""
        Console.set_use_pretty_prompts(False)
        assert Console._use_pretty_prompts is False

        Console.set_use_pretty_prompts(True)
        assert Console._use_pretty_prompts is True

    @patch("questionary.text")
    def test_prompt_input(self, mock_text):
        """Test prompting for input."""
        mock_text.return_value.ask.return_value = "test value"

        result = Console.prompt_input("Enter value:")

        assert result == "test value"
        mock_text.assert_called_once_with("Enter value:", default="")

    @patch("questionary.text")
    def test_prompt_input_with_default(self, mock_text):
        """Test prompting for input with default."""
        mock_text.return_value.ask.return_value = None

        result = Console.prompt_input("Enter value:", default="default")

        assert result == "default"

    @patch("questionary.confirm")
    def test_prompt_confirm_yes(self, mock_confirm):
        """Test prompting for confirmation (yes)."""
        mock_confirm.return_value.ask.return_value = True

        result = Console.prompt_confirm("Continue?")

        assert result is True
        mock_confirm.assert_called_once_with("Continue?", default=True)

    @patch("questionary.confirm")
    def test_prompt_confirm_no(self, mock_confirm):
        """Test prompting for confirmation (no)."""
        mock_confirm.return_value.ask.return_value = False

        result = Console.prompt_confirm("Continue?", default=False)

        assert result is False

    @patch("questionary.confirm")
    def test_prompt_confirm_none(self, mock_confirm):
        """Test prompting for confirmation (None returned, use default)."""
        mock_confirm.return_value.ask.return_value = None

        result = Console.prompt_confirm("Continue?", default=True)

        assert result is True

    @patch("questionary.select")
    def test_prompt_select(self, mock_select):
        """Test prompting to select from list."""
        mock_select.return_value.ask.return_value = "Option 2"

        result = Console.prompt_select("Choose:", ["Option 1", "Option 2", "Option 3"])

        assert result == "Option 2"
        mock_select.assert_called_once_with(
            "Choose:", choices=["Option 1", "Option 2", "Option 3"], default=None
        )

    @patch("questionary.select")
    def test_prompt_select_with_default(self, mock_select):
        """Test prompting to select from list with default."""
        mock_select.return_value.ask.return_value = "Option 1"

        result = Console.prompt_select(
            "Choose:", ["Option 1", "Option 2"], default="Option 1"
        )

        assert result == "Option 1"
