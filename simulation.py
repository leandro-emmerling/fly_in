#!/usr/bin/env python3


from pathfinder import Pathfinder
from map import Map
from drone import Drone
from zone import Zone
from connection import Connection


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
        self.zone_occupancy: dict[Zone, int] = self._count_zone_occupancy()
        self.connection_occupancy: dict[Connection, int] = (
            self._count_connection_occupancy())

    def _create_drones(self) -> list[Drone]:
        """Create nb_drones Drone objects, all starting at map.start.

        Returns:
            A list of drones as much as set in the config file.
        """
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
        """Compute the shared cheapest path and assigns it to every drone.

        Returns:
            A dict mapping each Drone to its planned route (list of Zones).

        Raises:
            PathNotFoundError: If no path exists between start and end.
        """
        path = self.pathfinder.find_path(self.map.start, self.map.end)
        return {drone: path.copy() for drone in self.drones}

    def run(self) -> list[list[str]]:
        """Runs the simulation turn by turn until every drone is delivered.

        Returns:
            A list of turns; each turn is a list of Movement strings in
            the format "D<id>-<zone>" for every drone that moved.
        """
        turns: list[list[str]] = []
        while not all(drone.current_zone is drone.target
                      for drone in self.drones):
            turn_moves: list[str] = []
            for drone in self.drones:
                if drone.current_zone is drone.target:
                    continue
                move = self._advance_drone(drone)
                if move is not None:
                    turn_moves.append(move)
            turns.append(turn_moves)
            self.connection_occupancy = self._count_connection_occupancy()
        return turns

    def _advance_drone(self, drone: Drone) -> str | None:
        """Gets the next zone from the current zone to generate the right
        output format for a single drone with its given ID.

        Args:
            drone: the Drone object which is checked.

        Returns:
            The right formatted String for the Output or 'None' if the drone
            is not able to move.
        """
        cur_ind: int = self.paths[drone].index(drone.current_zone)
        next_zone: Zone = self.paths[drone][cur_ind + 1]

        connect = next(
            entry for entry in self.pathfinder.adjacency[drone.current_zone]
            if entry.neighbor is next_zone).connection

        if (self.zone_occupancy[next_zone] < next_zone.max_drones) and (
            self.connection_occupancy[connect] < connect.max_link_capacity
        ):
            self.zone_occupancy[drone.current_zone] -= 1
            self.connection_occupancy[connect] += 1
            self.zone_occupancy[next_zone] += 1
            drone.current_zone = next_zone
            return f"{drone.drone_id}-{drone.current_zone.name}"
        else:
            return None

    def _count_zone_occupancy(self) -> dict[Zone, int]:
        """Counts how many drones currently occupy each zone.

        Returns:
            A dict mapping each Zone to the number of drones currently in it.
        """
        occupancy: dict[Zone, int] = {
            zone: 0 for zone in self.map.zones.values()}
        for drone in self.drones:
            occupancy[drone.current_zone] += 1
        return occupancy

    def _count_connection_occupancy(self) -> dict[Connection, int]:
        """Initialize how many drones occupy each connection with zero.

        Returns:
            A dict with the connection and the number of drones
            (here initialized with 0).
        """
        return {connection: 0 for connection in self.map.connections}
