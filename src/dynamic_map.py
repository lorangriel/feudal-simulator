"""Dynamic map view used by the simulator."""
import math
import random
import tkinter as tk
from tkinter import ttk
from typing import List

from constants import BORDER_COLORS, NEIGHBOR_NONE_STR
from node import Node


class DynamicMapCanvas:
    """A simplified dynamic map using random placement and lines."""

    def __init__(self, parent_frame, simulator, world_data):
        self.parent_frame = parent_frame
        self.simulator = simulator
        self.world_data = world_data
        self.canvas = None
        self.dynamic_scale = 1.0
        self.positions = {}  # node_id -> (x, y)
        self.tooltip = None

    def set_world_data(self, world_data):
        """Replace the internal reference to ``world_data``."""
        self.world_data = world_data

    def show(self):
        """Creates and displays the dynamic map canvas."""
        for w in self.parent_frame.winfo_children():
            w.destroy()

        self.parent_frame.grid_rowconfigure(0, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.parent_frame, bg="white", scrollregion=(0, 0, 3000, 2000))
        self.canvas.grid(row=0, column=0, sticky="nsew")

        xsc = tk.Scrollbar(self.parent_frame, orient="horizontal", command=self.canvas.xview)
        xsc.grid(row=1, column=0, sticky="ew")
        ysc = tk.Scrollbar(self.parent_frame, orient="vertical", command=self.canvas.yview)
        ysc.grid(row=0, column=1, sticky="ns")
        self.canvas.config(xscrollcommand=xsc.set, yscrollcommand=ysc.set)

        # Bottom button bar
        btn_fr = ttk.Frame(self.parent_frame, style="Tool.TFrame")
        btn_fr.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_fr, text="< Tillbaka", command=self.simulator.show_no_world_view).pack(side=tk.LEFT, padx=5)

        # Bind mouse wheel for zooming
        self.canvas.bind("<MouseWheel>", self.on_dynamic_map_zoom)
        self.canvas.bind("<Button-4>", self.on_dynamic_map_zoom)
        self.canvas.bind("<Button-5>", self.on_dynamic_map_zoom)

        self.draw_dynamic_map()

    def on_dynamic_map_zoom(self, event):
        """Zooms the dynamic map view."""
        if event.delta > 0 or event.num == 4:
            factor = 1.1
        else:
            factor = 0.9
        self.dynamic_scale *= factor
        self.dynamic_scale = max(0.1, min(self.dynamic_scale, 10.0))
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        zoom_x = self.canvas.canvasx(canvas_width / 2)
        zoom_y = self.canvas.canvasy(canvas_height / 2)
        self.canvas.scale("all", zoom_x, zoom_y, factor, factor)

    def draw_dynamic_map(self):
        """Draws Jarldoms and connections on the dynamic map."""
        self.canvas.delete("all")
        self.hide_tooltip()

        jarldomes: List[Node] = []
        if self.world_data and "nodes" in self.world_data:
            for node_id_str, nd in self.world_data["nodes"].items():
                try:
                    node_id = int(node_id_str)
                    if self.simulator.get_depth_of_node(node_id) == 3:
                        jarldomes.append(Node.from_dict(nd))
                except ValueError:
                    continue

        if not jarldomes:
            self.simulator.add_status_message("Inga Jarldömen att visa i dynamisk karta.")
            self.canvas.create_text(1500, 1000, text="Inga Jarldömen att visa.", anchor="center", font=("Arial", 12))
            return

        map_width = 3000
        map_height = 2000
        padding = 200
        self.positions = {}

        for nd in jarldomes:
            node_id = nd.node_id
            x = random.randint(padding, map_width - padding)
            y = random.randint(padding, map_height - padding)
            self.positions[node_id] = (x, y)

        node_polygons = {}
        for nd in jarldomes:
            jid = nd.node_id
            x, y = self.positions[jid]

            neighbor_count = 0
            for nb in nd.neighbors:
                nb_id = nb.id
                if isinstance(nb_id, int) and str(nb_id) in self.world_data.get("nodes", {}):
                    neighbor_count += 1

            sides = max(3, min(neighbor_count, 8))
            size = 40

            pts = []
            for k in range(sides):
                a_deg = (360 / sides) * k
                a_rad = math.radians(a_deg)
                px = x + size * math.cos(a_rad)
                py = y + size * math.sin(a_rad)
                pts.extend([px, py])

            color_fill = "#ffdddd"
            outline_color = "red"

            poly_id = self.canvas.create_polygon(pts, fill=color_fill, outline=outline_color, width=2)
            display_name = self.simulator.get_display_name_for_node(nd, 3)
            txt_id = self.canvas.create_text(x, y, text=display_name, fill="black", anchor="center")

            tag_dyn = f"dyn_{jid}"
            self.canvas.itemconfig(poly_id, tags=(tag_dyn,))
            self.canvas.itemconfig(txt_id, tags=(tag_dyn,))

            def on_click_node(event, n_id=jid):
                clicked_node = self.world_data["nodes"].get(str(n_id))
                if clicked_node:
                    self.simulator.show_node_view(clicked_node)

            self.canvas.tag_bind(tag_dyn, "<Double-Button-1>", on_click_node)
            self.canvas.tag_bind(tag_dyn, "<Enter>", lambda e, n=nd: self.show_node_tooltip(e, n))
            self.canvas.tag_bind(tag_dyn, "<Leave>", self.hide_tooltip)

            node_polygons[jid] = {"cx": x, "cy": y, "polygon_id": poly_id}

        self.draw_dynamic_lines(node_polygons)

    def draw_dynamic_lines(self, node_polygons):
        """Draws lines representing borders between Jarldoms."""
        drawn_pairs = set()

        if not self.world_data or "nodes" not in self.world_data:
            return

        for node_id_str, nd in self.world_data["nodes"].items():
            try:
                node_id = int(node_id_str)
            except ValueError:
                continue

            if self.simulator.get_depth_of_node(node_id) == 3 and "neighbors" in nd:
                node_obj = Node.from_dict(nd)
                A_id = node_id
                if A_id not in node_polygons:
                    continue

                A_cx = node_polygons[A_id]["cx"]
                A_cy = node_polygons[A_id]["cy"]

                for nb_info in node_obj.neighbors:
                    B_id = nb_info.id
                    if isinstance(B_id, int) and B_id in node_polygons:
                        if B_id != A_id and tuple(sorted((A_id, B_id))) not in drawn_pairs:
                            B_cx = node_polygons[B_id]["cx"]
                            B_cy = node_polygons[B_id]["cy"]

                            border_type = nb_info.border
                            color = BORDER_COLORS.get(border_type, "gray")
                            width = 2
                            if border_type in ["väg", "stor väg", "vattendrag"]:
                                width = 3
                            if border_type == "stor väg":
                                width = 4

                            self.canvas.create_line(A_cx, A_cy, B_cx, B_cy, fill=color, width=width)
                            drawn_pairs.add(tuple(sorted((A_id, B_id))))

    def show_node_tooltip(self, event, node: Node) -> None:
        """Display a small popup with information about ``node``."""
        display_name = self.simulator.get_display_name_for_node(node, 3)
        self._show_tooltip(event, display_name)

    def _show_tooltip(self, event, text: str) -> None:
        self.hide_tooltip()
        self.tooltip = tk.Toplevel(self.canvas)
        self.tooltip.wm_overrideredirect(True)
        label = ttk.Label(
            self.tooltip,
            text=text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            justify=tk.LEFT,
        )
        label.pack()
        self.tooltip.update_idletasks()
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None) -> None:
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

