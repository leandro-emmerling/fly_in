*This project has been created as part of the 42 curriculum by lemmerli.*

# fly_in

## Description

**fly_in** is an efficient drone routing system that navigates a fleet of drones through a network of connected zones, minimizing the total number of simulation turns required to move all drones from a central start zone to a target end zone.

The system reads a map file describing zones and connections, computes optimal paths using a weighted pathfinding algorithm, and runs a turn-based simulation that respects all movement constraints such as zone capacity limits, connection capacity limits, and restricted zone traversal rules.

The project provides two visual interfaces: an animated terminal output and a graphical GUI window.

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`

### Installation

```bash
make install
```

This creates a virtual environment and installs all required dependencies.

### Running the simulation

```bash
make run
```

Runs the simulation with the default `config.txt` map in automatic mode (1 second per turn).

```bash
make step
```

Runs the simulation in step mode — press Enter to advance each turn manually.

```bash
make run CONFIG=maps/easy/01_linear_path.txt
```

Run with a specific map file.

### GUI mode

```bash
make gui
```

Opens a graphical window displaying the zone network, connections, and drone positions animated turn by turn.

```bash
make gui-step
```

Runs the graphical window simulation in step mode — press the Button to advance each turn manually.

### Running the tests

```bash
make test
```

Runs the custom test runner, which covers:
- Parser error detection (invalid zone types, duplicate connections, missing hubs, etc.)
- Pathfinder error detection (no valid path, blocked zones)
- Benchmark performance tests against the targets defined in the subject (VII.7)

### Linting

```bash
make lint
```

Runs `flake8` and `mypy` with the required flags.

## Algorithm choices and implementation strategy

### Pathfinding: Dijkstra with priority tie-breaking

The core pathfinding algorithm is **Dijkstra's shortest path algorithm**, implemented from scratch without any graph libraries (as required by the subject constraints).

**Key design decisions:**

- **Adjacency list** (`AdjacencyEntry` NamedTuple): Built once at `Pathfinder` construction time and cached for reuse across all drones. Each entry stores the neighbor zone, movement cost, and the connection object, avoiding repeated lookups during pathfinding.
- **Weighted edges**: Movement cost is determined by the destination zone type (`normal`/`priority` = 1 turn, `restricted` = 2 turns, `blocked` = impassable).
- **Priority zone tie-breaking**: When two paths have equal cost, paths through `PriorityZone`s are preferred. This is implemented by storing `(cost, priority_score)` tuples instead of plain integers in the distance map — Python's lexicographic tuple comparison handles the tie-breaking automatically without any additional logic.
- **Blocked zone filtering**: `BlockedZone`s are excluded at the neighbor level (`is_passable()` check), so they never enter the search space.
- **Linear search**: The "unvisited" set uses `min()` with a lambda key for simplicity and guaranteed correctness. This gives O(V²) complexity, which is sufficient for the map sizes in this project.

### Simulation: Turn-based engine with capacity constraints

The simulation proceeds in discrete turns. At each turn, every drone attempts to advance one step along its pre-computed path.

**Key mechanisms:**

- **Zone occupancy tracking**: A `dict[Zone, int]` counts how many drones occupy each zone. Updated incrementally on each movement — no full recount per turn.
- **Connection occupancy tracking**: A `dict[Connection, int]` tracks simultaneous connection usage within a turn. Reset after each turn (except for connections currently occupied by in-transit drones on restricted zones).
- **Restricted zone 2-turn rule**: When a drone moves toward a `RestrictedZone`, it enters an `in_transit_to` state for one turn. The capacity of the target zone is reserved immediately on departure to prevent race conditions. The drone must arrive the following turn — it cannot wait on the connection.
- **Start/end zone exemption**: `start` and `end` zones are exempt from `max_drones` capacity limits, as specified in the subject (VII.2).
- **Structured output**: Movements are returned as `MoveResult` NamedTuples (drone ID + zone or connection), keeping simulation logic cleanly separated from display logic.

### Visual representation

**Terminal mode** (`display.py`):
- Turn-by-turn colored output using ANSI escape codes, with zone names in their configured color and drone IDs in a distinct drone color.
- Animated grid drawn with Unicode box-drawing characters, showing zone symbols, connection dots (interpolated between zone positions, alternating colors), drone counts per zone, and highlighted start (`S`) / end (`E`) zones.
- `--step` flag for manual turn-by-turn stepping.

**GUI mode** (`gui_display.py`):
- Built with `tkinter` (Python standard library, no additional dependencies).
- Zones rendered as colored rectangles with their name and type symbol.
- Connections drawn as two-color lines (each half in the color of its respective zone).
- Drones displayed as labeled circles on their current zone, or at the midpoint of a connection when in transit.
- Supports both automatic (1s/turn) and manual step mode.

## Resources

### References

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `abc` module documentation](https://docs.python.org/3/library/abc.html)
- [Python `tkinter` documentation](https://docs.python.org/3/library/tkinter.html)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [PEP 484 — Type hints](https://peps.python.org/pep-0484/)
- [ANSI escape codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)

### AI usage

Claude (Anthropic) was consulted selectively throughout this project as a conceptual resource when encountering unfamiliar topics.

Concretely, AI was used to:

- **Understand new concepts**: When encountering unfamiliar topics (e.g. graph algorithms, ANSI escape codes, `tkinter`), Claude was asked to explain the concept before the student attempted the implementation independently.
- **Clarify design questions**: Occasionally used to think through trade-offs between approaches (e.g. NamedTuple vs. plain dict), without receiving a direct recommendation or code.
- **Review reasoning**: After working through a problem, sometimes used to verify whether the conceptual understanding was correct — not to validate code.

All implementation decisions, architecture choices, and every line of code were made and written entirely by the student.
