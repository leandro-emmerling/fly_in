#!/usr/bin/env python3


from abc import ABC, abstractmethod


class Zone(ABC):
    """Abstract Class 'Zone'"""
    def __init__(
        self, name: str, x: int, y: int,
        color: str | None = None, max_drones: int = 1
                ) -> None:
        """Initialize the Zone with the parsed Arguments from parser.py.

        Args:
            name: The Zone that is parsed
            x: Value of the x-coordinate where the Zone is located.
            y: Value of the y-coordinate where the Zone is located.
            color: How the Zone is colored in the Map (default=None).
            max_drones: Number of drones that can occupy this zone
                        at the same time (default=1).
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.color: str | None = color
        self.max_drones: int = max_drones

    @abstractmethod
    def display_symbol(self) -> str:
        """Abstract Method for different Symbols per Zone."""
        pass

    def movement_cost(self) -> int:
        """By default the movement cost is 1 (except restricted Zone)."""
        return 1

    def is_passable(self) -> bool:
        """By default the possability to pass is True (except blocked Zone)."""
        return True

    def is_prioritised(self) -> bool:
        """By default value of priorisation is False (except priority Zone)."""
        return False


class NormalZone(Zone):
    """Normal Zone class that inhiterates from Motherclass 'Zone'."""

    def display_symbol(self) -> str:
        """Return the Symbol ('+') to dipslay the normal Zone."""
        return ("+")


class BlockedZone(Zone):
    """Blocked Zone class that inhiterates from Motherclass 'Zone'."""

    def display_symbol(self) -> str:
        """Return the Symbol ('#') to dipslay the blocked Zone."""
        return ("#")

    def is_passable(self) -> bool:
        """Blocked zone is no passable."""
        return False


class RestrictedZone(Zone):
    """Restriced Zone class that inhiterates from Motherclass 'Zone'."""

    def display_symbol(self) -> str:
        """Return the Symbol ('^') to dipslay the restricted Zone."""
        return ("^")

    def movement_cost(self) -> int:
        """Restricted zones cost 2 turns to enter."""
        return 2


class PriorityZone(Zone):
    """PriorityZone class that inhiterates from Motherclass 'Zone'."""

    def display_symbol(self) -> str:
        """Return the Symbol ('*') to dipslay the priority Zone."""
        return ("*")

    def is_prioritised(self) -> bool:
        """Priority Zone are prioritised ways"""
        return True
