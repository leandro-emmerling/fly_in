#!/usr/bin/env python3


import tkinter as tk
from map import Map
from zone import Zone
from parser import Parser
from pathfinder import Pathfinder



class GuiDisplay:
    """To display the colored turn output and the grid build from the
    given Map object and displayed it in the an external GUI Window.
    """
    PADDING = 20
    def __init__(self, game_map: Map) -> None:
        """Initialize the gui display class with the game_map.

        Args:
            game_map: The given map to pass all the required information.
        """
        self.root = tk.Tk()
        self.root.title("Fly_in")
        self.map = game_map
        self._setup_canvas()
        self._compute_grid_metrics()


    def _setup_canvas(self) -> None:
        self.canvas_width: int = 800
        self.canvas_height: int = 600
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width, height=self.canvas_height, bg="gray75")
        self.canvas.pack()

    def _compute_grid_metrics(self) -> None:
        self.min_x, self.min_y, self.max_x, self.max_y = self.map.get_grid_bounds()
        self.grid_width: int = self.max_x - self.min_x + 1
        self.grid_height: int = self.max_y - self.min_y + 1
        self.cell_size: float = min(
            (self.canvas_width - 2 * self.PADDING) / self.grid_width,
            (self.canvas_height -2 * self.PADDING) / self.grid_height)
        self.half_cs: float = self.cell_size / 2

    def _zone_to_pixel(self, zone: Zone) -> tuple[float, float]:
            mid_x: float = ((zone.x - self.min_x) * self.cell_size
                            + self.half_cs + self.PADDING)
            mid_y: float = ((zone.y - self.min_y) * self.cell_size
                            + self.half_cs + self.PADDING)
            return mid_x, mid_y

    def _get_text_color(self, zone) -> str:
        if zone.color is None:
            return "black"
        r, g, b = self.root.winfo_rgb(zone.color)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        if brightness < 32767:
            return "white"
        else:
            return "black"


    def _draw_grid(self) -> None:
        for i in range(self.grid_width + 1):
            x: int = i * self.cell_size + self.PADDING
            self.canvas.create_line(
                x, self.PADDING,
                x, self.grid_height * self.cell_size + self.PADDING, fill="grey")

        for j in range(self.grid_height + 1):
            y: int = j * self.cell_size + self.PADDING
            self.canvas.create_line(
                self.PADDING, y,
                self.grid_width * self.cell_size + self.PADDING, y, fill="grey")

    def _draw_zones(self, shrink: int = 0) -> None:
        for zone in self.map.zones.values():
            mid_x, mid_y = self._zone_to_pixel(zone)
            x1: float = mid_x - (self.half_cs - shrink)
            y1: float = mid_y - (self.half_cs - shrink)
            x2: float = mid_x + (self.half_cs - shrink)
            y2: float = mid_y + (self.half_cs - shrink)
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=zone.color if zone.color else "white", outline="")
            self.canvas.create_text(mid_x, mid_y - 7, text=zone.display_symbol(), fill=self._get_text_color(zone))
            self.canvas.create_text(mid_x, mid_y + 7, text=zone.name, fill=self._get_text_color(zone))

    def _draw_connections(self) -> None:
        for con in self.map.connections:
            x1, y1 = self._zone_to_pixel(con.zone_a)
            x2, y2 = self._zone_to_pixel(con.zone_b)
            self.canvas.create_line(
                x1, y1, (x1 + x2) / 2, (y1 + y2) / 2 , width=4, fill=con.zone_b.color if con.zone_b.color else "white")
            self.canvas.create_line(
                (x1 + x2) / 2, (y1 + y2) / 2 ,x2 , y2, width=4, fill=con.zone_a.color if con.zone_a.color else "white")

    def run(self) -> None:
        self._draw_grid()
        self._draw_zones(0)
        self._draw_connections()
        self._draw_zones(10)
        self.root.mainloop()


if __name__ == "__main__":
    file_parser = Parser()
    map = file_parser.parse("config.txt")
    gd = GuiDisplay(map)
    gd.run()

