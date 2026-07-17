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
