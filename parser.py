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
        """Parses the input file and returns a validated Map object.

        Args:
            filepath: Path to the input file to parse.

        Returns:
            A fully constructed and validated Map object.

        Raises:
            ParserError: If the file is malformed or incomplete.
            MapValidationError: If the resulting Map fails consistency checks.
        """
        with open(filepath) as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("#") or not line.rstrip():
                    continue
                prefix, rest = line.split(":", 1)
                rest = rest.rstrip()
                handler = self.handlers.get(prefix)
                if handler is None:
                    raise ParserError(
                        f"Line {line_number}: No valid prefix! ({prefix})")
                else:
                    handler(rest, line_number, prefix)
            if self.start is None:
                raise ParserError("Missing start_hub definition")
            if self.end is None:
                raise ParserError("Missing end_hub definition")
            if self.nb_drones is None:
                raise ParserError("Missing nb_drones definition")
            return Map(
                nb_drones=self.nb_drones,
                zones=self.zones_by_name,
                connections=self.connections,
                start=self.start,
                end=self.end
            )

    def _parse_nb_drones(
            self, line: str, line_number: int, _prefix: str) -> None:
        """Parses the raw string of nb_drones and sets it on the parser.

        Args:
            line: Raw string from the config file.
            line_number: Number of the line for error messages.

        Raises:
            ParserError: If nb_drones is malformed, non-positive, or
                already defined.
        """
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
        """Parses the raw string of the zone and
            creates a validated Zone object.

        Args:
            line: Raw string from the config file.
            line_number: Number of the line for error messages.
            prefix: The kind of zone object that will be created.

        Raises:
            ParserError: If a Zone is malformed or incomplete.
        """
        if prefix == "start_hub" and self.start is not None:
            raise ParserError(
                f"Line {line_number}: start_hub defined more than once!")
        if prefix == "end_hub" and self.end is not None:
            raise ParserError(
                f"Line {line_number}: end_hub defined more than once!")
        if "[" in line:
            pos_val, metadata = line.split("[", 1)
            metadata_dict: dict[str, str] = (
                self._parse_metadata(metadata, line_number)
                )
        else:
            pos_val = line
            metadata_dict = {}
        name, x, y = pos_val.split()
        try:
            x_int = int(x)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: x coordinate "
                f"must be a valid Integer! ({x})"
            )
        try:
            y_int = int(y)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: y coordinate "
                f"must be a valid Integer! ({y})"
            )
        zone_type = metadata_dict.get("zone", "normal")
        color = metadata_dict.get("color")
        max_drones = metadata_dict.get("max_drones", 1)
        try:
            max_drones_int = int(max_drones)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: max_drones "
                f"must be a valid Integer! ({max_drones})"
            )
        zone_class = self.zone_class.get(zone_type)
        if zone_class is None:
            raise ParserError(
                f"Line {line_number}: {zone_type} is no valid zone!"
            )
        zone = zone_class(
            name=name, x=x_int, y=y_int, color=color, max_drones=max_drones_int
            )
        self.zones_by_name[name] = zone
        if prefix == "start_hub":
            self.start = zone
        elif prefix == "end_hub":
            self.end = zone

    def _parse_connection(
            self, line: str, line_number: int,  _prefix: str) -> None:
        """Parses the raw string of the connection and
            creates a validated Connection object.

        Args:
            line: Raw string from the config file.
            line_number: Number of the line for error messages.

        Raises:
            ParserError: If connection is malformed or incomplete.
        """
        if "[" in line:
            pos_val, metadata = line.split("[", 1)
            metadata_dict: dict[str, str] = (
                self._parse_metadata(metadata, line_number)
            )
        else:
            pos_val = line
            metadata_dict = {}
        try:
            name_a, name_b = pos_val.split("-")
        except ValueError:
            raise ParserError(
                f"Line {line_number}: connection "
                "must be declared as 'zone_a-zone_b'"
            )
        name_a = name_a.strip()
        name_b = name_b.strip()
        zone_a = self.zones_by_name.get(name_a)
        if zone_a is None:
            raise ParserError(
                f"Line {line_number}: zone 'a' "
                f"must link only on predefined zones! ({name_a})"
            )
        zone_b = self.zones_by_name.get(name_b)
        if zone_b is None:
            raise ParserError(
                f"Line {line_number}: zone 'b' "
                f"must link only on predefined zones! ({name_b})"
            )
        max_link_capacity = metadata_dict.get("max_link_capacity", 1)
        try:
            max_link_capacity_int = int(max_link_capacity)
        except ValueError:
            raise ParserError(
                f"Line {line_number}: max. link capacity "
                f"must be a valid Integer! ({max_link_capacity})"
            )
        connection = Connection(zone_a=zone_a, zone_b=zone_b,
                                max_link_capacity=max_link_capacity_int)
        self.connections.append(connection)

    def _parse_metadata(
            self, raw_metadata: str, line_number: int) -> dict[str, str]:
        """Parses a metadata block into a dict.

        Args:
            raw_metadata: Raw string from the line in the config file.
            line_number: Number of the line for error messages.

        Returns:
            A formatted dict version of the metadata

        Raises:
            ParserError: If the block is malformed or incomplete
        """
        if raw_metadata[-1] == "]":
            raw_metadata = raw_metadata[:-1]
        else:
            raise ParserError(f"Line {line_number}: "
                              "Metadata needs a closing ']'")
        metadata: list[str] = raw_metadata.split()
        metadata_dict: dict[str, str] = {}
        for item in metadata:
            try:
                item, value = item.split("=")
            except ValueError:
                raise ParserError(
                    f"Line {line_number}: Metadata item and "
                    f"value must be separated only by '='"
                )
            metadata_dict[item] = value
        return metadata_dict
