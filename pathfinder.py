#!/usr/bin/env python3


from zone import Zone
from map import Map
from typing import NamedTuple
from error import PathNotFoundError


class AdjacencyEntry(NamedTuple):
    """A single reachable neighbor with the cost to enter it"""
    neighbor: Zone
    cost: int


class Pathfinder:
    """..."""
    def __init__(self, game_map: Map):
        self.map = game_map
        self.adjacency = self._build_adjacency()

    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        """Finds the cheapest path from start to end using Dijkstra's algorithm.

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
        distances: dict[Zone, float] = {
            zone: float("inf") for zone in self.map.zones.values()}
        distances[start] = 0
        previous: dict[Zone, float] = {}
        unvisited: set[Zone] = {zone for zone in self.map.zones.values()}
        while unvisited:
            current: Zone = min(unvisited, key=lambda zone: distances[zone])
            unvisited.remove(current)
            if current is end:
                break
            for entry in self.adjacency[current]:
                if entry.neighbor not in unvisited:
                    continue
                if not entry.neighbor.is_passable():
                    continue
                new_cost: float = distances[current] + entry.cost
                if new_cost < distances[entry.neighbor]:
                    distances[entry.neighbor] = new_cost
                    previous[entry.neighbor] = current
        if distances[end] == float("inf"):
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
                AdjacencyEntry(neighbor=zone_b, cost=zone_b.movement_cost()))
            adjacency[zone_b].append(
                AdjacencyEntry(neighbor=zone_a, cost=zone_a.movement_cost()))
        return adjacency
