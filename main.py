#!/usr/bin/env python3


from parser import Parser
from error import ParserError, MapValidationError, PathNotFoundError
from pathfinder import Pathfinder
from simulation import Simulation
from terminal_colors import TerminalColors


if __name__ == "__main__":
    turn_count = 0
    tc = TerminalColors()
    try:
        p = Parser()
        game_map = p.parse("config.txt")
        pf = Pathfinder(game_map)
        sim = Simulation(game_map, pf)
        path = pf.find_path(game_map.start, game_map.end)
        for turn in sim.run():
            turn_count += 1
            print(f"Turn {turn_count}: ", end="")
            print(*turn)
    except (ParserError, MapValidationError) as e:
        print(tc.colorize(f"Error: {e}", "red"))
        exit(1)
    except PathNotFoundError as e:
        print(f"No path: {e}")
        exit(1)
    print("Path found:")
    print(" -> ".join(zone.name for zone in path))
    print(f"Total cost: {sum(zone.movement_cost() for zone in path[1:])}")
