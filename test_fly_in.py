#!/usr/bin/env python3

from pathlib import Path
from parser import Parser
from pathfinder import Pathfinder
from simulation import Simulation
from error import ParserError, PathNotFoundError, MapValidationError


MAPS_DIR = Path(__file__).parent / "maps"
PARSER_DIR = MAPS_DIR / "parser"
PATHFINDER_DIR = MAPS_DIR / "pathfinder"


def run_parser_tests() -> None:
    tests = [
        "test_dash_in_name.txt",
        "test_invalid_zone_type.txt",
        "test_duplicate_zone_name.txt",
        "test_invalid_nb_drones.txt",
        "test_unknown_zone_connection.txt",
        "test_invalid_capacity.txt",
        "test_missing_start.txt",
        "test_missing_end.txt",
        "test_missing_nb_drones.txt",
        "test_duplicate_start.txt",
        "test_duplicate_end.txt",
        "test_zero_drones.txt",
        "test_unknown_metadata_key.txt",
        "test_self_connection.txt",
    ]
    print("\n=========== Parser Tests ===========\n")
    for filename in tests:
        try:
            Parser().parse(str(PARSER_DIR / filename))
            print(f"X {filename}: kein Fehler geworfen!")
        except (ParserError, MapValidationError) as e:
            print(f"{filename}: {type(e).__name__} ({e})")
        except Exception as e:
            print(f"!!! {filename}: "
                  f"unerwarteter Fehler: {type(e).__name__}: {e}")
    print()


def run_pathfinder_tests() -> None:
    tests = [
        "test_blocked_zone.txt",
        "test_no_path.txt"
    ]
    print("\n=========== Pathfinder Tests ===========\n")
    for filename in tests:
        try:
            game_map = Parser().parse(str(PATHFINDER_DIR / filename))
            pf = Pathfinder(game_map)
            pf.find_path(game_map.start, game_map.end)
            print(f"X {filename}: kein Fehler geworfen!")
        except (PathNotFoundError, MapValidationError) as e:
            print(f"{filename}: {type(e).__name__} ({e})")
        except Exception as e:
            print(f"!!! {filename}: "
                  f"unerwarteter Fehler: {type(e).__name__}: {e}")
    print()


def run_benchmark_tests() -> None:
    maps = [
        ("maps/easy/01_linear_path.txt", 6),
        ("maps/easy/02_simple_fork.txt", 6),
        ("maps/easy/03_basic_capacity.txt", 8),
        ("maps/medium/01_dead_end_trap.txt", 15),
        ("maps/medium/02_circular_loop.txt", 20),
        ("maps/medium/03_priority_puzzle.txt", 12),
        ("maps/hard/01_maze_nightmare.txt", 45),
        ("maps/hard/02_capacity_hell.txt", 60),
        ("maps/hard/03_ultimate_challenge.txt", 35),
        ("maps/challenger/01_the_impossible_dream.txt", 45),
    ]
    print("\n=========== Benchmark Tests ===========\n")
    for filepath, target in maps:
        game_map = Parser().parse(filepath)
        pf = Pathfinder(game_map)
        sim = Simulation(game_map, pf)
        turns, _ = sim.run()
        status = "Bestanden!" if len(turns) <= target else "Leider verkackt..."
        print(f"{status}\n {filepath}: {len(turns)} turns (target: {target})")


if __name__ == "__main__":
    run_parser_tests()
    run_pathfinder_tests()
    run_benchmark_tests()
