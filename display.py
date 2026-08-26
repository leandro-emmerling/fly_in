#!/usr/bin/env python3


from terminal_colors import TerminalColors
from map import Map
from simulation import MoveResult
from typing import NamedTuple
from zone import Zone
import time


class GridBounds(NamedTuple):
    """Coordinates for the bounds of the grid."""
    min_x: int
    min_y: int
    max_x: int
    max_y: int


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

    def _get_grid_bounds(self) -> GridBounds:
        """Calculates the smallest x/y coordinates and the highest x/y
        coordinates to get the bounds of the grid.

        Returns:
            A GridBounds instance with its min. and max. x/y coordinates.
        """
        zones = self.map.zones.values()
        min_x = min(zones, key=lambda zone: zone.x).x
        min_y = min(zones, key=lambda zone: zone.y).y
        max_x = max(zones, key=lambda zone: zone.x).x
        max_y = max(zones, key=lambda zone: zone.y).y
        return GridBounds(min_x, min_y, max_x, max_y)

    def _build_grid(self, drone_state: dict[str, Zone]) -> list[list[str]]:
        """Builds a 2D grid from the map zones and drone positions.

        Args:
            drone_state: A dict mapping each drone_id to its current zone.

        Returns:
            A 2D list of colored strings representing the grid,
            with zones at their normalized coordinates and drones
            overlaid at their current positions.
        """
        min_x, min_y, max_x, max_y = self._get_grid_bounds()
        width: int = max_x - min_x + 1
        height: int = max_y - min_y + 1
        grid: list[list[str]] = []
        for y in range(height):
            row: list[str] = []
            for x in range(width):
                row.append("  ")
            grid.append(row)
        for zone in self.map.zones.values():
            grid[zone.y - min_y][zone.x - min_x] = (
                self.colors.colorize(zone.display_symbol() + " ", zone.color)
            )
        occupancy: dict[Zone, int] = {
            zone: 0 for zone in self.map.zones.values()}
        for zone in drone_state.values():
            occupancy[zone] += 1
        for zone, count in occupancy.items():
            if count > 0:
                grid[zone.y - min_y][zone.x - min_x] = (
                    self.colors.colorize(
                        str(count) + " ", self.colors.drone_color)
                )
        return grid

    def display_grid(self) -> None:
        """"Prints the map grid with a double-line border to the terminal."""
        grid: list[list[str]] = self._build_grid()
        width: int = len(grid[0])
        print("╔" + "═" * (width * 2) + "╗")
        for row in grid:
            print("║" + "".join(row) + "║")
        print("╚" + "═" * (width * 2) + "╝")

    def display_animated(
        self, turns: list[list[MoveResult]],
        drone_states: list[dict[str, Zone]], step: bool = False) -> None:
        """Displays the simulation turn by turn with an animated grid.

        Args:
            turns: The list of turns from Simulation.run()
            drone_states: A list of drone position snapshots, one per turn.
            step: Flag for automatic or manuel turn steps
        """
        for turn_index, turn in enumerate(turns, start=1):
            grid: list[list[str]] = self._build_grid(
                drone_states[turn_index - 1])
            height: int = len(grid)
            width: int = len(grid[0])
            formatted_moves = [self._format_move(move) for move in turn]
            print(f"Turn {turn_index}:", *formatted_moves, end="\033[K\n")
            print("╔" + "═" * (width * 2) + "╗")
            for row in grid:
                print("║" + "".join(row) + "║")
            print("╚" + "═" * (width * 2) + "╝")
            if step:
                input("Press Enter for next turn...")
                print("\033[1A\033[K", end="")
            else:
                time.sleep(1)
            if turn_index < len(turns):
                print(f"\033[{height + 2}A", end="")
