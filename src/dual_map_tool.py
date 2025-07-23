"""Simplified dual map tool for feudal domains.

This module implements a minimal mapping application with two
synchronised map views:
- Map A: static hex grid with drag and drop, colouring and border editing.
- Map B: relationship map showing connections between nodes.

The code focuses on demonstrating the requested behaviour rather than
providing a full featured editor.  It is intentionally self contained
so it can be run directly with ``python src/dual_map_tool.py``.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox

# ------------------------------------------------------------
# Data structures
# ------------------------------------------------------------

BORDER_TYPES = [
    "<Ingen>",
    "liten v\u00e4g",
    "v\u00e4g",
    "stor v\u00e4g",
    "vildmark",
    "tr\u00e4sk",
    "berg",
    "vattendrag",
]

PALETTE = [
    "lightyellow",
    "gold",
    "orange",
    "tomato",
    "lightblue",
    "deepskyblue",
    "palegreen",
    "orchid",
    "tan",
    "wheat",
    "plum",
    "lightgray",
]

SAVE_FILE = "dual_map_world.json"


@dataclass
class Node:
    """Simple representation of a domain node."""

    node_id: int
    name: str
    parent_id: Optional[int] = None
    row: int = 0
    col: int = 0
    color: str = "lightyellow"
    neighbors: List[int] = field(default_factory=list)
    borders: Dict[int, str] = field(default_factory=dict)  # neighbor_id -> border


class World:
    """Manages nodes and handles persistence."""

    def __init__(self) -> None:
        self.nodes: Dict[int, Node] = {}
        self.next_id = 1

    def save(self, path: str = SAVE_FILE) -> None:
        data = {
            "next_id": self.next_id,
            "nodes": {nid: asdict(n) for nid, n in self.nodes.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str = SAVE_FILE) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.next_id = raw.get("next_id", 1)
        self.nodes = {int(k): Node(**v) for k, v in raw.get("nodes", {}).items()}

    def add_node(self, name: str, parent_id: Optional[int], row: int, col: int) -> Node:
        nid = self.next_id
        self.next_id += 1
        node = Node(nid, name, parent_id, row, col)
        self.nodes[nid] = node
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].neighbors.append(nid)
            node.neighbors.append(parent_id)
        return node

    def copy_state(self) -> Dict[int, dict]:
        return {nid: asdict(n) for nid, n in self.nodes.items()}

    def restore_state(self, state: Dict[int, dict]) -> None:
        self.nodes = {int(nid): Node(**nd) for nid, nd in state.items()}
        self.next_id = max(self.nodes.keys(), default=0) + 1


class History:
    """Simple undo/redo history."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.undo_stack: List[Dict[int, dict]] = []
        self.redo_stack: List[Dict[int, dict]] = []
        self.limit = 50

    def push(self) -> None:
        self.undo_stack.append(self.world.copy_state())
        if len(self.undo_stack) > self.limit:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self) -> None:
        if not self.undo_stack:
            return
        self.redo_stack.append(self.world.copy_state())
        state = self.undo_stack.pop()
        self.world.restore_state(state)

    def redo(self) -> None:
        if not self.redo_stack:
            return
        self.undo_stack.append(self.world.copy_state())
        state = self.redo_stack.pop()
        self.world.restore_state(state)


# ------------------------------------------------------------
# Map A: Hex grid view
# ------------------------------------------------------------

class HexMap(ttk.Frame):
    """Hex grid map with drag/drop and colouring."""

    def __init__(self, master, world: World, history: History, callback):
        super().__init__(master)
        self.world = world
        self.history = history
        self.callback = callback  # called when node selected
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.hex_size = 30
        self.drag_data: Tuple[int, int] | None = None
        self.selected_color = PALETTE[0]
        self.bind_events()
        self.redraw()

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)

    def hex_to_xy(self, row: int, col: int) -> Tuple[float, float]:
        step_y = self.hex_size * math.sqrt(3)
        step_x = self.hex_size * 1.5
        x = col * step_x + 50
        y = row * step_y + 50 + (self.hex_size * math.sqrt(3) / 2 if col % 2 else 0)
        return x, y

    def xy_to_hex(self, x: float, y: float) -> Tuple[int, int]:
        step_y = self.hex_size * math.sqrt(3)
        step_x = self.hex_size * 1.5
        col = int(round((x - 50) / step_x))
        row = int(round((y - 50 - (self.hex_size * math.sqrt(3) / 2 if col % 2 else 0)) / step_y))
        return row, col

    def draw_hex(self, row: int, col: int, color: str, nid: int) -> None:
        cx, cy = self.hex_to_xy(row, col)
        points = []
        for i in range(6):
            ang = math.radians(60 * i - 30)
            px = cx + self.hex_size * math.cos(ang)
            py = cy + self.hex_size * math.sin(ang)
            points.extend([px, py])
        tag = f"hex_{nid}"
        self.canvas.create_polygon(points, fill=color, outline="black", tags=tag)
        self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(tag, "<ButtonPress-3>", self.on_right_click)
        self.canvas.tag_bind(tag, "<Double-Button-1>", self.on_double_click)

    def redraw(self) -> None:
        self.canvas.delete("all")
        for nid, node in self.world.nodes.items():
            self.draw_hex(node.row, node.col, node.color, nid)
        for nid, node in self.world.nodes.items():
            cx, cy = self.hex_to_xy(node.row, node.col)
            self.canvas.create_text(cx, cy, text=str(nid), tags=f"hex_{nid}")

    def on_press(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item)
        for t in tags:
            if t.startswith("hex_"):
                nid = int(t.split("_")[1])
                self.drag_data = (nid, event.x, event.y)
                self.callback(nid)
                break

    def on_drag(self, event):
        if not self.drag_data:
            return
        nid, sx, sy = self.drag_data
        dx = event.x - sx
        dy = event.y - sy
        self.canvas.move(f"hex_{nid}", dx, dy)
        self.drag_data = (nid, event.x, event.y)

    def on_release(self, event):
        if not self.drag_data:
            return
        nid, _, _ = self.drag_data
        self.drag_data = None
        row, col = self.xy_to_hex(event.x, event.y)
        node = self.world.nodes[nid]
        if any((n.row, n.col) == (row, col) for n in self.world.nodes.values() if n.node_id != nid):
            messagebox.showerror("Ogiltig", "Platsen \u00e4r redan upptagen")
            self.redraw()
            return
        conflicts = 0
        for nb in node.neighbors:
            if nb in self.world.nodes:
                nbn = self.world.nodes[nb]
                if abs(nbn.row - row) > 1 or abs(nbn.col - col) > 1:
                    conflicts += 1
        if conflicts:
            res = messagebox.askyesnocancel(
                "Konflikt",
                f"Flytten bryter {conflicts} grannrelationer. L\u00f6s dem?",
            )
            if res is None:
                self.redraw()
                return
            if res:
                for nb in list(node.neighbors):
                    nbn = self.world.nodes.get(nb)
                    if nbn and (abs(nbn.row - row) > 1 or abs(nbn.col - col) > 1):
                        node.neighbors.remove(nb)
                        if nid in nbn.neighbors:
                            nbn.neighbors.remove(nid)
        node.row = row
        node.col = col
        self.history.push()
        self.world.save()
        self.redraw()

    def on_double_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item)
        for t in tags:
            if t.startswith("hex_"):
                nid = int(t.split("_")[1])
                self.callback(nid)
                break

    def on_right_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item)
        nid = None
        for t in tags:
            if t.startswith("hex_"):
                nid = int(t.split("_")[1])
                break
        if nid is None:
            return
        menu = tk.Menu(self, tearoff=0)
        for bt in BORDER_TYPES:
            menu.add_command(
                label=bt,
                command=lambda b=bt, n=nid: self.set_border(n, b, event),
            )
        menu.post(event.x_root, event.y_root)

    def set_border(self, nid: int, border_type: str, event) -> None:
        node = self.world.nodes[nid]
        row, col = node.row, node.col
        ang = math.degrees(
            math.atan2(event.y - self.hex_to_xy(row, col)[1], event.x - self.hex_to_xy(row, col)[0])
        )
        direction = int(((ang + 360 + 30) % 360) / 60)
        dirs = [(-1, 0), (-1, 1), (0, 1), (1, 0), (0, -1), (-1, -1)]
        dr, dc = dirs[direction % 6]
        nb_row = row + dr
        nb_col = col + dc
        nb_node = None
        for nb in self.world.nodes.values():
            if nb.row == nb_row and nb.col == nb_col:
                nb_node = nb
                break
        if nb_node:
            node.borders[nb_node.node_id] = border_type
            nb_node.borders[nid] = border_type
        self.history.push()
        self.world.save()
        self.redraw()

    def set_color(self, color: str) -> None:
        self.selected_color = color

    def color_hex(self, nid: int) -> None:
        if nid not in self.world.nodes:
            return
        node = self.world.nodes[nid]
        node.color = self.selected_color
        self.history.push()
        self.world.save()
        self.redraw()

    def on_zoom(self, event):
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        self.canvas.scale("all", event.x, event.y, factor, factor)

    def on_pan_start(self, event):
        self._pan_start = (event.x, event.y)

    def on_pan_move(self, event):
        if not hasattr(self, "_pan_start"):
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self.canvas.scan_dragto(-dx, -dy, gain=1)
        self._pan_start = (event.x, event.y)


# ------------------------------------------------------------
# Map B: relationship view
# ------------------------------------------------------------

class RelationMap(ttk.Frame):
    """Displays nodes grouped by overlord."""

    def __init__(self, master, world: World, callback):
        super().__init__(master)
        self.world = world
        self.callback = callback
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.scale = 1.0
        self.bind_events()
        self.redraw()

    def bind_events(self):
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)

    def redraw(self):
        self.canvas.delete("all")
        groups: Dict[Optional[int], List[Node]] = {}
        for n in self.world.nodes.values():
            groups.setdefault(n.parent_id, []).append(n)
        x = 50
        y = 50
        for parent, nodes in groups.items():
            if parent:
                self.canvas.create_text(x + 40, y - 20, text=f"Overlord {parent}")
            for i, node in enumerate(nodes):
                cx = x + i * 80
                cy = y
                count = len(node.neighbors)
                tag = f"rel_{node.node_id}"
                if count <= 1:
                    self.canvas.create_oval(cx - 20, cy - 20, cx + 20, cy + 20, fill=node.color, outline="black", tags=tag)
                elif count == 2:
                    self.canvas.create_rectangle(cx - 20, cy - 20, cx + 20, cy + 20, fill=node.color, outline="black", tags=tag)
                elif count == 3:
                    pts = [cx, cy - 20, cx - 20, cy + 20, cx + 20, cy + 20]
                    self.canvas.create_polygon(pts, fill=node.color, outline="black", tags=tag)
                else:
                    self.canvas.create_polygon(cx - 20, cy - 20, cx + 20, cy - 20, cx + 20, cy + 20, cx - 20, cy + 20, fill=node.color, outline="black", tags=tag)
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, n=node.node_id: self.callback(n))
            y += 80

    def on_zoom(self, event):
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        self.scale *= factor
        self.canvas.scale("all", event.x, event.y, factor, factor)

    def on_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item)
        for t in tags:
            if t.startswith("rel_"):
                nid = int(t.split("_")[1])
                self.callback(nid)
                break

    def on_pan_start(self, event):
        self._pan_start = (event.x, event.y)

    def on_pan_move(self, event):
        if not hasattr(self, "_pan_start"):
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self.canvas.scan_dragto(-dx, -dy, gain=1)
        self._pan_start = (event.x, event.y)


# ------------------------------------------------------------
# Main application
# ------------------------------------------------------------

class DualMapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dual Map Tool")
        self.geometry("1000x700")

        self.world = World()
        self.world.load()
        self.history = History(self.world)

        self.create_ui()
        self.selected_node: Optional[int] = None

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew")

        self.hex_map = HexMap(notebook, self.world, self.history, self.on_select)
        notebook.add(self.hex_map, text="Karta")

        self.rel_map = RelationMap(notebook, self.world, self.on_select)
        notebook.add(self.rel_map, text="Relationer")

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="ns")
        ttk.Label(right, text="F\u00e4rg").pack(pady=5)
        for c in PALETTE:
            btn = tk.Button(right, bg=c, width=2, command=lambda col=c: self.hex_map.set_color(col))
            btn.pack(fill="x")
        ttk.Button(right, text="Undo", command=self.undo).pack(pady=10, fill="x")
        ttk.Button(right, text="Redo", command=self.redo).pack(fill="x")
        self.info = tk.Label(right, text="")
        self.info.pack(pady=20)

    def on_select(self, nid: int):
        self.selected_node = nid
        node = self.world.nodes.get(nid)
        if not node:
            return
        self.info.config(text=f"ID: {nid}\nRow: {node.row} Col: {node.col}\nF\u00e4rg: {node.color}")
        self.hex_map.color_hex(nid)
        self.rel_map.redraw()

    def undo(self):
        self.history.undo()
        self.hex_map.redraw()
        self.rel_map.redraw()
        self.world.save()

    def redo(self):
        self.history.redo()
        self.hex_map.redraw()
        self.rel_map.redraw()
        self.world.save()


if __name__ == "__main__":
    app = DualMapApp()
    if not app.world.nodes:
        for r in range(3):
            for c in range(3):
                app.world.add_node(f"Node {r}-{c}", None, r, c)
        app.history.push()
        app.world.save()
    app.mainloop()
