#!/usr/bin/env python3


from pathfinder import Pathfinder
from map import Map
from drone import Drone
from zone import Zone


class Simulation:
    """Simulate the different drones depending on the connections"""
    def __init__(self, game_map: Map, pathfinder: Pathfinder) -> None:
        """Initialize the simulation class with the connections and drones

        Args:
            game_map: the map object where the drones will fly through.
            pathfinder: algorithm for path finding.
        """
        self.map = game_map
        self.pathfinder = pathfinder
        self.drones: list[Drone] = self._create_drones()
        self.paths: dict[Drone, list[Zone]] = self._compute_initial_paths()

    def _create_drones(self) -> list[Drone]:
        """Create nb_drones Drone objects, all starting at map.start."""
        drones: list[Drone] = []
        for i in range(self.map.nb_drones):
            drone = Drone(
                drone_id=f"D{i + 1}",
                current_zone=self.map.start,
                target=self.map.end
            )
            drones.append(drone)
        return drones

    def _compute_initial_paths(self) -> dict[Drone, list[Zone]]:
        """Compute the initial cheapest path for every drone."""
        ...
