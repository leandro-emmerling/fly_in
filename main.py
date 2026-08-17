#!/usr/bin/env python3


from parser import Parser
from error import ParserError, MapValidationError, PathNotFoundError
from pathfinder import Pathfinder


if __name__ == "__main__":
    p = Parser()
    try:
        game_map = p.parse("config.txt")
        pf = Pathfinder(game_map)
        path = pf.find_path(game_map.start, game_map.end)
    except (ParserError, MapValidationError) as e:
        print(f"Error: {e}")
        exit(1)
    except PathNotFoundError as e:
        print(f"No path: {e}")
        exit(1)
    print("Path found:")
    print(" -> ".join(zone.name for zone in path))
    print(f"Total cost: {sum(zone.movement_cost() for zone in path[1:])}")
