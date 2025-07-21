# -*- coding: utf-8 -*-
"""Logic for calculating map positions and borders."""

from __future__ import annotations

from collections import deque
import math
from typing import Dict, List, Tuple

from constants import BORDER_COLORS, NEIGHBOR_NONE_STR


class StaticMapLogic:
    """Handle placement of Jarldoms on a hex grid."""

    def __init__(self, world_data: Dict[str, any], rows: int = 30, cols: int = 30,
                 hex_size: int = 30, spacing: int = 15) -> None:
        self.world_data = world_data
        self.rows = rows
        self.cols = cols
        self.hex_size = hex_size
        self.spacing = spacing
        self.map_static_positions: Dict[int, Tuple[int, int]] = {}
        self.static_grid_occupied: List[List[int | None]] = [
            [None] * self.cols for _ in range(self.rows)
        ]

    # --------------------------------------------------
    # Placement
    # --------------------------------------------------
    def place_jarldomes_bfs(self, get_depth_of_node) -> None:
        """Place Jarldoms using BFS based on neighbor connections."""
        jarldomes: Dict[int, dict] = {}
        for node_id_str, nd in self.world_data.get("nodes", {}).items():
            try:
                nid = int(node_id_str)
            except ValueError:
                continue
            if get_depth_of_node(nid) == 3:
                jarldomes[nid] = nd

        adjacency: Dict[int, List[int]] = {}
        for jid, nd in jarldomes.items():
            neighbors: List[int] = []
            for nb in nd.get("neighbors", []):
                nbid = nb.get("id")
                if isinstance(nbid, int) and nbid in jarldomes:
                    neighbors.append(nbid)
            adjacency[jid] = neighbors

        self.map_static_positions = {}
        self.static_grid_occupied = [
            [None] * self.cols for _ in range(self.rows)
        ]
        visited: set[int] = set()

        def get_hex_neighbors(r: int, c: int) -> List[Tuple[int, int]]:
            neighbors = []
            if c % 2 == 0:
                offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)]
            else:
                offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1)]
            for dr, dc in offsets:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr, nc))
            return neighbors

        def bfs_component(start_jid: int, start_r: int, start_c: int) -> None:
            queue = deque([(start_jid, start_r, start_c)])
            self.map_static_positions[start_jid] = (start_r, start_c)
            self.static_grid_occupied[start_r][start_c] = start_jid
            visited.add(start_jid)
            while queue:
                current_jid, r, c = queue.popleft()
                for neighbor_jid in adjacency.get(current_jid, []):
                    if neighbor_jid not in visited:
                        for nr, nc in get_hex_neighbors(r, c):
                            if self.static_grid_occupied[nr][nc] is None:
                                self.map_static_positions[neighbor_jid] = (nr, nc)
                                self.static_grid_occupied[nr][nc] = neighbor_jid
                                visited.add(neighbor_jid)
                                queue.append((neighbor_jid, nr, nc))
                                break

        for jid in list(jarldomes.keys()):
            if jid not in visited:
                found_start = False
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.static_grid_occupied[r][c] is None:
                            bfs_component(jid, r, c)
                            found_start = True
                            break
                    if found_start:
                        break
                if not found_start:
                    # out of space - ignore placement
                    pass

    # --------------------------------------------------
    # Helper calculations
    # --------------------------------------------------
    def hex_center(self, r: int, c: int) -> Tuple[float, float]:
        row_step = self.hex_size * math.sqrt(3) + self.spacing
        col_step = self.hex_size * 1.5 + self.spacing
        x_offset = 50
        y_offset = 50
        cx = x_offset + c * col_step
        cy = y_offset + r * row_step + (row_step / 2 if c % 2 else 0)
        return cx, cy

    def border_lines(self) -> List[Tuple[float, float, float, float, str, int]]:
        """Return list of lines between neighbors."""
        lines: List[Tuple[float, float, float, float, str, int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                jid = self.static_grid_occupied[r][c]
                if jid is None:
                    continue
                node = self.world_data.get("nodes", {}).get(str(jid))
                if not node:
                    continue
                cx_a, cy_a = self.hex_center(r, c)
                for nb in node.get("neighbors", []):
                    nbid = nb.get("id")
                    if isinstance(nbid, int) and nbid > jid and nbid in self.map_static_positions:
                        r2, c2 = self.map_static_positions[nbid]
                        cx_b, cy_b = self.hex_center(r2, c2)
                        color = BORDER_COLORS.get(nb.get("border", NEIGHBOR_NONE_STR), "gray")
                        width = 3 if color in ["black", "brown", "blue"] else 2
                        lines.append((cx_a, cy_a, cx_b, cy_b, color, width))
        return lines
