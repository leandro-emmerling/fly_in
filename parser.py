#!/usr/bin/env python3


from typing import Callable
from zone import Zone, NormalZone, BlockedZone, RestrictedZone, PriorityZone
from connection import Connection
from map import Map
from error import ParserError


class Parser:
    """Mother class 'Parser' to pass and validate the Arguments."""
    def __init__(self) -> None:
        """Initialize the parser with the source file."""
        self.zones_by_name: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start: Zone | None = None
        self.end: Zone | None = None
        self.nb_drones: int | None = None
        self.handlers: dict[str, Callable[..., None]] = {
            "nb_drones": self._parse_nb_drones,
            "start_hub": self._parse_zone,
            "end_hub": self._parse_zone,
            "hub": self._parse_zone,
            "connection": self._parse_connection
        }
        self.zone_class: dict[str, type[Zone]] = {
            "normal": NormalZone,
            "blocked": BlockedZone,
            "restricted": RestrictedZone,
            "priority": PriorityZone
        }

    def parse(self, filepath: str) -> Map:
        pass

    def _parse_nb_drones(self, line: str, line_number: int) -> None:
        pass

    def _parse_zone(self, line: str, line_number: int) -> None:
        sliced_line: list[str] = []
        sliced_line = line.split("[", 1)

    def _parse_connection(self, line: str, line_number: int) -> None:
        pass
