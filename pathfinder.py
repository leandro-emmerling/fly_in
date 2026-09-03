#!/usr/bin/env python3


from zone import Zone
from map import Map
from typing import NamedTuple
from connection import Connection
from error import PathNotFoundError


class AdjacencyEntry(NamedTuple):
    """A single reachable neighbor with the cost to enter it."""
    neighbor: Zone
    cost: int
    connection: Connection


class Pathfinder:
    """Find and return the cheapest path with each zone and
    its reachable neighbors.
    """
    def __init__(self, game_map: Map) -> None:
        """Initialize the Pathfinder with the given map and build the adjacency list.

        Args:
            game_map: The map containing zones and connections to navigate.
        """
        self.map = game_map
        self.adjacency = self._build_adjacency()

    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        """Find the cheapest path from start to end using Dijkstra's algorithm.

        Args:
            start: The zone to start from.
            end: The target zone.

        Returns:
            An ordered list of Zone objects representing the cheapest path
            from start to end (inclusive of both).

        Raises:
            PathNotFoundError: If no path exists between start and end.
        """
        if start is end:
            return [start]
        distances: dict[Zone, tuple[float, int]] = {
            zone: (float("inf"), 0) for zone in self.map.zones.values()}
        distances[start] = (0, 0)
        previous: dict[Zone, Zone] = {}
        unvisited: set[Zone] = {zone for zone in self.map.zones.values()}
        while unvisited:
            current: Zone = min(unvisited, key=lambda zone: distances[zone][0])
            unvisited.remove(current)
            if current is end:
                break
            for entry in self.adjacency[current]:
                if entry.neighbor not in unvisited:
                    continue
                if not entry.neighbor.is_passable():
                    continue
                new_cost: float = distances[current][0] + entry.cost
                new_priority_score = (
                    distances[cusrrent][1] + (
                        -1 if entry.neighbor.is_prioritised() else 0)
                    )
                new_total = (new_cost, new_priority_score)
                if new_total < distances[entry.neighbor]:
                    distances[entry.neighbor] = new_total
                    previous[entry.neighbor] = current
        if distances[end][0] == float("inf"):
            raise PathNotFoundError("No valid path to the end-zone found!")
        path: list[Zone] = [end]
        current = end
        while current is not start:
            current = previous[current]
            path.append(current)
        path.reverse()
        return path

    def _build_adjacency(self) -> dict[Zone, list[AdjacencyEntry]]:
        """Builds an adjacency map from each zone to its reachable neighbors.

        Returns:
            A dict mapping each zone to a list of AdjacencyEntry objects
            representing its directly connected neighbors and their costs.
        """
        adjacency: dict[Zone, list[AdjacencyEntry]] = {}
        for zone in self.map.zones.values():
            adjacency[zone] = []
        for connection in self.map.connections:
            zone_a = connection.zone_a
            zone_b = connection.zone_b
            adjacency[zone_a].append(
                AdjacencyEntry(
                    neighbor=zone_b, cost=zone_b.movement_cost(),
                    connection=connection))
            adjacency[zone_b].append(
                AdjacencyEntry(
                    neighbor=zone_a, cost=zone_a.movement_cost(),
                    connection=connection))
        return adjacency
