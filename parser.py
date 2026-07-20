#!/usr/bin/env python3


from typing import Callable
from zone import Zone, NormalZone, BlockedZone, RestrictedZone, PriorityZone
from connection import Connection
from map import Map
from error import ParserError
from sys import exit


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
        with open(filepath) as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("#") or not line.rstrip():
                    continue
                raw: list = line.split(":", 1)
                prefix, rest = raw
                rest = rest.rstrip()
                handler = self.handlers.get(prefix)
                if handler is None:
                    raise ParserError(f"Line {line_number}: No valid prefix! ({prefix})")
                else:
                    handler(rest, line_number, prefix)

                

    def _parse_nb_drones(self, line: str, line_number: int, _prefix: str) -> None:
        if self.nb_drones is not None:
            raise ParserError(f"Line {line_number}: nb_drones defined more than once!")
        try:
            line_int: int = int(line)
        except ValueError:
            raise ParserError(f"Line {line_number}: nb_drones must be a valid Integer!")
        if line_int <= 0:
            raise ParserError(f"Line {line_number}: nb_drones must be greater than Zero!")
        self.nb_drones = line_int

    def _parse_zone(self, line: str, line_number: int, prefix: str) -> None:
        print(line, line_number)
        sliced_line: list[str] = line.split("[", 1)

    def _parse_connection(self, line: str, line_number: int,  prefix: str) -> None:
        pass


if __name__ == "__main__":
    p = Parser()
    try:
        p.parse("config.txt")
    except ParserError as e:
        print(f"Error: {e}")
        exit(1)