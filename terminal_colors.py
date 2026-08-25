#!/usr/bin/env python3


class TerminalColors:
    """Color palette for the Terminal Output."""
    def __init__(self) -> None:
        """Initialize the Class with a dict of the different color and
        its ANSI-Escape Codes.
        """
        self._colors: dict[str, str] = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "gray": "\033[90m",
            "orange": "\033[38;5;208m",
            "purple": "\033[38;5;129m",
            "pink": "\033[38;5;213m",
            "brown": "\033[38;5;130m",
            "lime": "\033[38;5;154m",
            "teal": "\033[38;5;30m",
            "navy": "\033[38;5;17m",
            "gold": "\033[38;5;220m",
            "turquoise": "\033[38;5;80m",
            "violet": "\033[38;5;177m",
            "maroon": "\033[38;5;88m"
        }
        self.reset: str = "\033[0m"
        self.drone_color: str = "\033[38;5;82m"
        self._fallback_color: str = "\033[38;5;250m"

    def get_color(self, color_name: str | None) -> str:
        """Looks up the ANSI code for a color name, with a fallback default.

        Args:
            color_name: The color name from the zone metadata (may be None).

        Returns:
            The matching ANSI escape code, or a default if unknown/None.
        """
        if color_name is None:
            return self._colors["white"]
        return self._colors.get(color_name, self._fallback_color)

    def colorize(self, text: str, color_name: str | None) -> str:
        """Wraps text in the ANSI code for a color, followed by a reset.

        Args:
            text: The text to colorize.
            color_name: The color name to apply (may be None for default)

        Returns:
            The text wrapped in the matching ANSi color code and reset.
        """
        return f"{self.get_color(color_name)}{text}{self.reset}"
