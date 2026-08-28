#!/usr/bin/env python3


from zone import Zone
from connection import Connection
from error import MapValidationError


class Map:
    """Class 'Map' to generate a ... Objekt"""
    def __init__(
        self, nb_drones: int, zones: dict[str, Zone],
        connections: list[Connection], start: Zone, end: Zone
                ) -> None:
        """Initialize the Map with the parsed Arguments from parser.py.

        Args:
            nb_drones: Number of Drones using.
            zones: a dictionary of zones returned from zone.py.
            connections: a list of connection objects.
            start: the start zone object.
            end: the end zone object.
        """
        self.nb_drones: int = nb_drones
        self.zones: dict[str, Zone] = zones
        self.connections: list[Connection] = connections
        self.start: Zone = start
        self.end: Zone = end
        self.validate()
        self._apply_special_zone_rules()

    def validate(self) -> None:
        """Validation of map object if the arguments are solid."""
        errors: list[str] = []
        seen_pairs: set[frozenset[str]] = set()
        for connection in self.connections:
            if connection.zone_a.name not in self.zones:
                errors.append(f"Connection references to unknown Zone: "
                              f"{connection.zone_a.name}")
            if connection.zone_b.name not in self.zones:
                errors.append(f"Connection references to unknown Zone: "
                              f"{connection.zone_b.name}")
            pair = frozenset({connection.zone_a.name, connection.zone_b.name})
            if pair in seen_pairs:
                errors.append(f"Double connection found: {pair}")
            else:
                seen_pairs.add(pair)
        if errors:
            raise MapValidationError("\n".join(errors))

    def _apply_special_zone_rules(self) -> None:
        """Sets max_drones for start and end to nb_drones.

        Start and end zones are exempt from normal capacity limits:
        all drones may begin there, and multiple drones may arrive
        at the end simultaneously.
        """
        self.start.max_drones = self.nb_drones
        self.end.max_drones = self.nb_drones

    def get_grid_bounds(self) -> tuple[int, int, int, int]:
        """Calculates the smallest x/y coordinates and the highest x/y
        coordinates to get the bounds of the grid.

        Returns:
            A tuple instance with its min. and max. x/y coordinates.
        """
        zones = self.zones.values()
        min_x = min(zones, key=lambda zone: zone.x).x
        min_y = min(zones, key=lambda zone: zone.y).y
        max_x = max(zones, key=lambda zone: zone.x).x
        max_y = max(zones, key=lambda zone: zone.y).y
        return min_x, min_y, max_x, max_y
