#!/usr/bin/env python3


from pathfinder import Pathfinder
from map import Map
from drone import Drone
from zone import Zone
from connection import Connection
from typing import NamedTuple


class MoveResult(NamedTuple):
    """Information about a single drone's movement in a turn.

    Exactly one of `zone` or `connection` is set, depending on
    whether the drone completed a normal move or departed toward
    a restricted zone.
    """
    drone_id: str
    zone: Zone | None
    connection: Connection | None


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
            self._compute_connection_occupancy())

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

    def run(self) -> tuple[list[list[MoveResult]], list[dict[str, Zone]]]:
        """Runs the simulation turn by turn until every drone is delivered.

        Returns:
            - A list of turns; each turn is a list of MoveResult objects,
            one for every drone that moved during that turn.
            - A list of drone state snapshots, one per turn, mapping
            each drone_id to its current zone.
        """
        turns: list[list[MoveResult]] = []
        drone_states: list[dict[str, Zone]] = []
        while not all(drone.current_zone is drone.target
                      for drone in self.drones):
            turn_moves: list[MoveResult] = []
            for drone in self.drones:
                if drone.current_zone is drone.target:
                    continue
                move = self._advance_drone(drone)
                if move is not None:
                    turn_moves.append(move)
            turns.append(turn_moves)
            drone_states.append(
                {drone.drone_id: drone.current_zone for drone in self.drones})
            self.connection_occupancy = self._compute_connection_occupancy()
        return turns, drone_states

    def _advance_drone(self, drone: Drone) -> MoveResult | None:
        """Attempts to move a drone one step forward along its path.

        Args:
            drone: the Drone object which is checked.

        Returns:
            A MoveResult object with the drone_id and the Zone or Connection
            of its turn, or 'None' if the drone is not able to move.
        """
        if drone.in_transit_to is not None:
            restricted_zone: Zone = drone.in_transit_to
            drone.current_zone = restricted_zone
            drone.in_transit_to = None
            return MoveResult(
                drone_id=drone.drone_id, zone=restricted_zone, connection=None
                )
        cur_ind: int = self.paths[drone].index(drone.current_zone)
        next_zone: Zone = self.paths[drone][cur_ind + 1]
        connect = next(
            part for part in self.pathfinder.adjacency[drone.current_zone]
            if part.neighbor is next_zone).connection

        if next_zone.movement_cost() == 2:
            if (self.zone_occupancy[next_zone] < next_zone.max_drones) and (
                self.connection_occupancy[connect] < connect.max_link_capacity
            ):
                self.zone_occupancy[drone.current_zone] -= 1
                self.zone_occupancy[next_zone] += 1
                self.connection_occupancy[connect] += 1
                drone.in_transit_to = next_zone
                return MoveResult(
                    drone_id=drone.drone_id, zone=None, connection=connect
                )
            else:
                return None
        elif (self.zone_occupancy[next_zone] < next_zone.max_drones) and (
            self.connection_occupancy[connect] < connect.max_link_capacity
        ):
            self.zone_occupancy[drone.current_zone] -= 1
            self.connection_occupancy[connect] += 1
            self.zone_occupancy[next_zone] += 1
            drone.current_zone = next_zone
            return MoveResult(
                drone_id=drone.drone_id, zone=drone.current_zone,
                connection=None)
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

    def _compute_connection_occupancy(self) -> dict[Connection, int]:
        """Counts how many drones occupy each connection, hold values
        of 'in_transit'-connection and initialize it with zero.

        Returns:
            A dict with the connection and the number of drones
            (initialized with 0).
        """
        in_transit_connections: set[Connection] = set()
        for drone in self.drones:
            if drone.in_transit_to is None:
                continue
            connection = next(
                part for part in self.pathfinder.adjacency[drone.current_zone]
                if part.neighbor is drone.in_transit_to
            ).connection
            in_transit_connections.add(connection)
        if not in_transit_connections:
            return {connection: 0 for connection in self.map.connections}
        new_occupancy: dict[Connection, int] = {}
        for con in self.map.connections:
            if con in in_transit_connections:
                new_occupancy[con] = self.connection_occupancy[con]
            else:
                new_occupancy[con] = 0
        return new_occupancy
