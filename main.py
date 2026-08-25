#!/usr/bin/env python3


from parser import Parser
from error import ParserError, MapValidationError, PathNotFoundError
from pathfinder import Pathfinder
from simulation import Simulation
from terminal_colors import TerminalColors
from display import Display


def main() -> None:
    """Run the main program."""
    tc = TerminalColors()
    try:
        parser = Parser()
        map = parser.parse("config.txt")
        pathfinder = Pathfinder(map)
        simulation = Simulation(map, pathfinder)
        display = Display(map)
        turns = simulation.run()
        display.display_turns(turns)
    except (ParserError, MapValidationError) as e:
        print(tc.colorize(f"Error: {e}", "red"))
        exit(1)
    except PathNotFoundError as e:
        print(tc.colorize(f"No path: {e}", "red"))
        exit(1)


if __name__ == "__main__":
    main()
