#!/usr/bin/env python3


import tkinter as tk
from map import Map
from zone import Zone
from parser import Parser
from pathfinder import Pathfinder
from simulation import MoveResult, Simulation


class GuiDisplay:
    """To display the colored turn output and the grid build from the
    given Map object and displayed it in the an external GUI Window.
    """
    PADDING = 20

    def __init__(self, game_map: Map, step: bool = False) -> None:
        """Initialize the gui display class with the game_map.

        Args:
            game_map: The given map to pass all the required information.
        """
        self.step = step
        self.root = tk.Tk()
        self.root.title("Fly_in")
        self.map = game_map
        self.pathfinder = Pathfinder(game_map)
        self.simulation = Simulation(game_map, self.pathfinder)
        self._setup_canvas()
        self._compute_grid_metrics()

    def _setup_canvas(self) -> None:
        """Sets up the tkinter canvas, label and optional step button."""
        self.canvas_width: int = 800
        self.canvas_height: int = 600
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width,
            height=self.canvas_height, bg="gray75")
        self.canvas.pack()
        self.label = tk.Label(self.root, text="")
        self.label.pack()
        if self.step:
            self.next_button = tk.Button(
                self.root, text="Next Turn", command=self._animate)
            self.next_button.pack(side="bottom", anchor="e")

    def _compute_grid_metrics(self) -> None:
        """Computes cell size and grid dimensions based on zone coordinates."""
        self.min_x, self.min_y, max_x, max_y = self.map.get_grid_bounds()
        self.grid_width: int = max_x - self.min_x + 1
        self.grid_height: int = max_y - self.min_y + 1
        self.cell_size: float = min(
            (self.canvas_width - 2 * self.PADDING) / self.grid_width,
            (self.canvas_height - 2 * self.PADDING) / self.grid_height)
        self.half_cs: float = self.cell_size / 2

    def _zone_to_pixel(self, zone: Zone) -> tuple[float, float]:
        """Converts zone grid coordinates to pixel coordinates on the canvas.

        Args:
            zone: The zone to convert.

        Returns:
            A tuple of (x, y) pixel coordinates for the zone center.
        """
        mid_x: float = ((zone.x - self.min_x) * self.cell_size
                        + self.half_cs + self.PADDING)
        mid_y: float = ((zone.y - self.min_y) * self.cell_size
                        + self.half_cs + self.PADDING)
        return mid_x, mid_y

    def _get_text_color(self, zone: Zone) -> str:
        """Returns black or white text color based on the zone background brightness.

        Args:
            zone: The zone whose color is evaluated.

        Returns:
            'white' for dark backgrounds, 'black' for light backgrounds.
        """
        if zone.color is None:
            return "black"
        r, g, b = self.root.winfo_rgb(zone.color)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        if brightness < 32767:
            return "white"
        else:
            return "black"

    def _draw_grid(self) -> None:
        """Draws the background grid lines on the canvas."""
        for i in range(self.grid_width + 1):
            x: float = i * self.cell_size + self.PADDING
            self.canvas.create_line(
                x, self.PADDING, x,
                self.grid_height * self.cell_size + self.PADDING, fill="grey")
        for j in range(self.grid_height + 1):
            y: float = j * self.cell_size + self.PADDING
            self.canvas.create_line(
                self.PADDING, y,
                self.grid_width * self.cell_size + self.PADDING,
                y, fill="grey")

    def _draw_zones(self, shrink: int = 0) -> None:
        """Draws all zones as colored rectangles with their name and symbol.

        Args:
            shrink: Pixel amount to shrink the rectangle on each side.
        """
        for zone in self.map.zones.values():
            mid_x, mid_y = self._zone_to_pixel(zone)
            x1: float = mid_x - (self.half_cs - shrink)
            y1: float = mid_y - (self.half_cs - shrink)
            x2: float = mid_x + (self.half_cs - shrink)
            y2: float = mid_y + (self.half_cs - shrink)
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=zone.color if zone.color else "white", outline="")
            self.canvas.create_text(
                mid_x, mid_y - 20,
                text=zone.display_symbol(), fill=self._get_text_color(zone))
            self.canvas.create_text(
                mid_x, mid_y - 8,
                text=zone.name, fill=self._get_text_color(zone))

    def _draw_connections(self) -> None:
        """Draws connections between zones as two-colored lines."""
        for con in self.map.connections:
            x1, y1 = self._zone_to_pixel(con.zone_a)
            x2, y2 = self._zone_to_pixel(con.zone_b)
            self.canvas.create_line(
                x1, y1, (x1 + x2) / 2, (y1 + y2) / 2, width=4,
                fill=con.zone_b.color if con.zone_b.color else "white")
            self.canvas.create_line(
                (x1 + x2) / 2, (y1 + y2) / 2, x2, y2, width=4,
                fill=con.zone_a.color if con.zone_a.color else "white")

    def display_animated(
        self, turns: list[list[MoveResult]],
            drone_states: list[dict[str, Zone]]) -> None:
        """Displays the simulation turn by turn with an animated grid.

        Args:
            turns: The list of turns from Simulation.run()
            drone_states: A list of drone position snapshots, one per turn.
        """
        self.turn_index: int = 0
        if self.turn_index == 0:
            self.turns = turns
            self.drone_states = drone_states
        self._animate()

    def _animate(self) -> None:
        """Renders the current turn and schedules or waits for the next."""
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_zones(0)
        self._draw_connections()
        self._draw_zones(10)
        self.turn_index += 1
        formatted_moves = []
        in_transit: set[str] = set()
        for move in self.turns[self.turn_index - 1]:
            formatted_moves.append(self._format_moves(move))
            if move.connection is not None:
                in_transit.add(move.drone_id)
                x1, y1 = self._zone_to_pixel(move.connection.zone_a)
                x2, y2 = self._zone_to_pixel(move.connection.zone_b)
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                self.canvas.create_oval(mid_x - 20, mid_y - 20 + 22,
                                        mid_x + 20, mid_y + 20 + 16,
                                        fill="lightgrey", outline="black")
                self.canvas.create_text(
                    mid_x, mid_y + 16, text=move.drone_id, fill="black")
        label_text = f"Turn {self.turn_index}: " + " ".join(formatted_moves)
        self.label.config(text=label_text)
        self._draw_drones(in_transit)
        if self.turn_index < len(self.turns):
            if self.step:
                pass
            else:
                self.root.after(1000, self._animate)
        elif self.turn_index == len(self.turns) and self.step:
            self.next_button.config(state="disabled")

    def _draw_drones(self, in_transit: set[str]) -> None:
        """Draws drone indicators on their current zones, skipping in-transit drones.

        Args:
            in_transit: Set of drone IDs currently traversing a connection.
        """
        for id, zone in self.drone_states[self.turn_index - 1].items():
            if id in in_transit:
                continue
            mid_x, mid_y = self._zone_to_pixel(zone)
            radius: float = 20
            self.canvas.create_oval(mid_x - radius, mid_y - radius + 22,
                                    mid_x + radius, mid_y + radius + 16,
                                    fill="lightgrey", outline="black")
            self.canvas.create_text(mid_x, mid_y + 16, text=id, fill="black")

    def _format_moves(self, move: MoveResult) -> str:
        """Formats a single MoveResult into a output string.

        Args:
            move: The MoveResult to format.

        Returns:
            A  string in "D<id>-<zone>" or "D<id>-<connection>" format.
        """
        if move.zone is not None:
            zone = move.zone
            return f"{move.drone_id}-{zone.name}"
        elif move.connection is not None:
            connection = move.connection
            zone_a = connection.zone_a
            zone_b = connection.zone_b
            return f"{move.drone_id}-{zone_a.name}-{zone_b.name}"
        else:
            raise ValueError("Invalid MoveResult")

    def run(self) -> None:
        """Run the main Programm"""
        self.root.mainloop()
