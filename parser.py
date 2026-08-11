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
                    raise ParserError(
                        f"Line {line_number}: No valid prefix! ({prefix})")
                else:
                    handler(rest, line_number, prefix)

    def _parse_nb_drones(
            self, line: str, line_number: int, _prefix: str) -> None:
        if self.nb_drones is not None:
            raise ParserError(
                f"Line {line_number}: nb_drones defined more than once!")
        try:
            nb: int = int(line)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: nb_drones must be a valid Integer!")
        if nb <= 0:
            raise ParserError(
                f"Line {line_number}: nb_drones must be greater than Zero!")
        self.nb_drones = nb

    def _parse_zone(self, line: str, line_number: int, prefix: str) -> None:
        if prefix == "start_hub" and self.start is not None:
            raise ParserError(
                f"Line: {line_number}: start_hub defined more than once!")
        if prefix == "end_hub" and self.end is not None:
            raise ParserError(
                f"Line: {line_number}: end_hub defined more than once!")
        if "[" in line:
            pos_val, metadata = line.split("[", 1)
            metadata_dict: dict[str, str] = self._parse_metadata(metadata, line_number)
        else:
            pos_val = line
            metadata_dict = {}
        name, x, y = pos_val.split()
        zone_type = metadata_dict.get("zone", "normal")
        color = metadata_dict.get("color")
        max_drones = int(metadata_dict.get("max_drones", 1))
        zone_class = self.zone_class[zone_type]
        zone = zone_class(
            name=name, x=int(x), y=int(y), color=color, max_drones=max_drones)
        self.zones_by_name[name] = zone
        if prefix == "start_hub":
            self.start = zone
        elif prefix == "end_hub":
            self.end = zone

    def _parse_connection(
            self, line: str, line_number: int,  prefix: str) -> None:
        pass

    def _parse_metadata(self, raw_metadata: str, line_number: int) -> dict[str, str]:
        """Parses a '[key=value key=value]' block into a dict."""
        if raw_metadata[-1] == "]":
            raw_metadata = raw_metadata[:-1]
        else:
            raise ParserError(f"Line: {line_number}: Metadata needs a closing ']'")
        try:
            metadata: list = raw_metadata.split()
        except ValueError:
            raise ParserError(
                f"Line: {line_number}: Metadata need this format "
                f"'[zone=<type> color=<value> max_drones=<number>]'"
                )
        metadata_dict: dict[str, str] = {}
        for item in metadata:
            try:
                item, value = item.split("=")
            except ValueError:
                raise ParserError(
                    f"Line: {line_number}: Metadata item and "
                    f"value must be seperated by '='"
                )
            metadata_dict[item] = value
        return metadata_dict

if __name__ == "__main__":
    p = Parser()
    try:
        p.parse("config.txt")
    except ParserError as e:
        print(f"Error: {e}")
        exit(1)
