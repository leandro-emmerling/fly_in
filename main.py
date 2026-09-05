#!/usr/bin/env python3


from parser import Parser
from error import ParserError, MapValidationError, PathNotFoundError
from pathfinder import Pathfinder
from simulation import Simulation
from terminal_colors import TerminalColors
from terminal_display import TerminalDisplay
from gui_display import GuiDisplay
import argparse


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments with config path and step flag.
    """
    parser = argparse.ArgumentParser(description="Fly-in drone simulation")
    parser.add_argument("config", help="Path to the config file")
    parser.add_argument("--step", action="store_true",
                        help="Step through turns manually with Enter")
    parser.add_argument("--gui", action="store_true",
                        help="Run the gui interface")
    return parser.parse_args()


def main() -> None:
    """Run the main program."""
    args = parse_args()
    tc = TerminalColors()
    try:
        file_parser = Parser()
        map = file_parser.parse(args.config)
        pathfinder = Pathfinder(map)
        simulation = Simulation(map, pathfinder)
        turns, drone_states = simulation.run()
        stats = simulation.get_stats(turns)
        if args.gui:
            gui = GuiDisplay(map, args.step)
            gui.display_animated(turns, drone_states, stats)
            gui.run()
        else:
            terminal = TerminalDisplay(map)
            terminal.display_animated(turns, drone_states, stats, args.step)

    except (ParserError, MapValidationError) as e:
        print(tc.colorize(f"Error: {e}", "red"))
        exit(1)
    except PathNotFoundError as e:
        print(tc.colorize(f"No path: {e}", "red"))
        exit(1)


if __name__ == "__main__":
    main()
