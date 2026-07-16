#!/usr/bin/env python3


from zone import Zone


class Connection:
    """For check if the connection between 2 Zones is valid"""
    def __init__(
        self, zone_a: Zone, zone_b: Zone,
        max_link_capacity: int = 1
                ) -> None:
        """Initialize the connection class with 2 Zones.

        Args:
            zone_a: The first Zone that is parsed.
            zone_b: The second Zone that is parsed.
            max_link_capacity: Maximum drones that can traverse this connection
        """
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity

    def get_other_zone(self, zone: Zone) -> Zone:
        """Returns the zone on the other end of this connection."""
        if (zone is not self.zone_a) and (zone is not self.zone_b):
            raise ValueError("You have to take in a valid Zone "
                             "that is part of the connection")
        return self.zone_b if zone is self.zone_a else self.zone_a
