#!/usr/bin/env python3


from zone import Zone


class Drone:
    """Create a Drone object with its id and target information."""
    def __init__(
            self, drone_id: str, current_zone: Zone, target: Zone) -> None:
        """Initialize the drone class with the main information.

        Args:
            drone_id: Number to identify every drone.
            current_zone: The actual zone the drone is in.
            target: The end zone where the drone will fly to.
        """
        self.drone_id: str = drone_id
        self.current_zone: Zone = current_zone
        self.target: Zone = target
        self.in_transit_to: Zone | None = None
