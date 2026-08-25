#!/usr/bin/env python3


from terminal_colors import TerminalColors
from map import Map
from simulation import MoveResult, Simulation
from pathfinder import Pathfinder


class Display:
    """To display the colored turn output and the grid
    build from the given Map object.
    """
    def __init__(self, game_map: Map) -> None:
        """Initialize the display class with the game_map.

        Args:
            game_map: The given map to pass all the required information.
        """
        self.map = game_map
        self.colors = TerminalColors()

    def _format_move(self, move: MoveResult) -> str:
        """Formats a single MoveResult into a colored output string.

        Args:
            move: The MoveResult to format.

        Returns:
            A colored string in "D<id>-<zone>" or "D<id>-<connection>" format.
        """
        drone_part = (f"{self.colors.drone_color}"
                      f"{move.drone_id}{self.colors.reset}")
        if move.zone is not None:
            zone = move.zone
            return (f"{drone_part}-"
                    f"{self.colors.colorize(zone.name, zone.color)}")
        else:
            connection = move.connection
            zone_a = connection.zone_a
            zone_b = connection.zone_b
            return (f"{drone_part}-"
                    f"{self.colors.colorize(zone_a.name, zone_a.color)}-"
                    f"{self.colors.colorize(zone_b.name, zone_b.color)}")

    def display_turns(self, turns: list[list[MoveResult]]) -> None:
        """Prints each turn's movements as a colored, formatted line.

        Args:
            turns: The list of turns from Simulation.run().
        """
        for turn_number, turn in enumerate(turns, start=1):
            formatted_moves = [self._format_move(move) for move in turn]
            print(f"Turn {turn_number}:", *formatted_moves)