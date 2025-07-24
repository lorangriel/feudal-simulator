# -*- coding: utf-8 -*-
"""Logic for calculating map positions and borders."""

from __future__ import annotations

from collections import deque
import math
from typing import Dict, List, Tuple

from constants import BORDER_COLORS, NEIGHBOR_NONE_STR, MAX_NEIGHBORS


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

        adjacency: Dict[int, List[Tuple[int, int]]] = {}
        for jid, nd in jarldomes.items():
            neighbors: List[Tuple[int, int]] = []
            for idx, nb in enumerate(nd.get("neighbors", [])):
                nbid = nb.get("id")
                if isinstance(nbid, int) and nbid in jarldomes:
                    # Store neighbor id with its slot index (1-6)
                    neighbors.append((nbid, idx + 1))
            adjacency[jid] = neighbors

        self.map_static_positions = {}
        self.static_grid_occupied = [
            [None] * self.cols for _ in range(self.rows)
        ]
        visited: set[int] = set()


        def bfs_component(start_jid: int) -> None:
            """Place all nodes in a connected component starting from ``start_jid``.

            The component is first explored in an unbounded coordinate system so
            that neighbors to the west or north don't get clamped by the grid
            edges. After the relative positions are determined, the entire
            component is shifted to the first available location that fits inside
            the grid."""

            queue = deque([(start_jid, 0, 0)])
            relative: Dict[int, Tuple[int, int]] = {start_jid: (0, 0)}
            visited.add(start_jid)

            while queue:
                current_jid, r, c = queue.popleft()
                for neighbor_jid, slot in adjacency.get(current_jid, []):
                    if neighbor_jid in relative:
                        continue
                    dr, dc = self.direction_offset(slot, c)
                    nr, nc = r + dr, c + dc
                    relative[neighbor_jid] = (nr, nc)
                    visited.add(neighbor_jid)
                    queue.append((neighbor_jid, nr, nc))

            min_r = min(r for r, _ in relative.values())
            max_r = max(r for r, _ in relative.values())
            min_c = min(c for _, c in relative.values())
            max_c = max(c for _, c in relative.values())
            height = max_r - min_r + 1
            width = max_c - min_c + 1

            placed = False
            for base_r in range(self.rows - height + 1):
                if placed:
                    break
                for base_c in range(self.cols - width + 1):
                    ok = True
                    for r, c in relative.values():
                        ar = base_r + (r - min_r)
                        ac = base_c + (c - min_c)
                        if self.static_grid_occupied[ar][ac] is not None:
                            ok = False
                            break
                    if ok:
                        for jid, (r, c) in relative.items():
                            ar = base_r + (r - min_r)
                            ac = base_c + (c - min_c)
                            self.map_static_positions[jid] = (ar, ac)
                            self.static_grid_occupied[ar][ac] = jid
                        placed = True
                        break

            if not placed:
                # Fallback: place nodes sequentially wherever space permits
                for jid, _ in relative.items():
                    for r in range(self.rows):
                        for c in range(self.cols):
                            if self.static_grid_occupied[r][c] is None:
                                self.map_static_positions[jid] = (r, c)
                                self.static_grid_occupied[r][c] = jid
                                break

        for jid in list(jarldomes.keys()):
            if jid not in visited:
                bfs_component(jid)

    def place_jarldomes_hierarchy(self, get_depth_of_node) -> None:
        """Place Jarldoms grouped by their hierarchy in the world tree."""
        nodes = self.world_data.get("nodes", {})

        groups: Dict[int | None, Dict[int | None, List[int]]] = {}

        for nid_str, nd in nodes.items():
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            if get_depth_of_node(nid) != 3:
                continue
            hertig_id = nd.get("parent_id")
            furste_id = None
            if hertig_id is not None and str(hertig_id) in nodes:
                furste_id = nodes[str(hertig_id)].get("parent_id")
            groups.setdefault(furste_id, {}).setdefault(hertig_id, []).append(nid)

        self.map_static_positions = {}
        self.static_grid_occupied = [[None] * self.cols for _ in range(self.rows)]

        border_pad = 1  # keep groups away from the map edges
        row = border_pad
        FUR_GAP = 5
        HER_GAP = 2
        for _fur_id, h_dict in groups.items():
            col = border_pad
            fur_height = 0
            for _her_id, j_list in h_dict.items():
                cluster_rows = int(math.ceil(math.sqrt(len(j_list)))) or 1
                cluster_cols = int(math.ceil(len(j_list) / cluster_rows)) or 1
                for j_idx, jid in enumerate(sorted(j_list)):
                    r = row + (j_idx // cluster_cols)
                    c = col + (j_idx % cluster_cols)
                    while r >= self.rows:
                        self.static_grid_occupied.append([None] * self.cols)
                        self.rows += 1
                    while c >= self.cols:
                        for rr in self.static_grid_occupied:
                            rr.append(None)
                        self.cols += 1
                    self.map_static_positions[jid] = (r, c)
                    self.static_grid_occupied[r][c] = jid
                fur_height = max(fur_height, cluster_rows)
                col += cluster_cols + HER_GAP
            row += fur_height + FUR_GAP

    # --------------------------------------------------
    # Helper calculations
    # --------------------------------------------------

    def direction_offset(self, direction: int, c: int) -> Tuple[int, int]:
        """Return ``(dr, dc)`` for moving from a column ``c`` in ``direction``.

        Directions use the convention: 1=N, 2=NE, 3=SE, 4=S, 5=SW, 6=NW.
        Offsets depend on column parity for the slanted sides of the hex grid.
        """
        if direction == 1:
            return -1, 0
        if direction == 4:
            return 1, 0
        if c % 2 == 0:
            if direction == 2:
                return -1, 1
            if direction == 3:
                return 0, 1
            if direction == 5:
                return 0, -1
            if direction == 6:
                return -1, -1
        else:
            if direction == 2:
                return 0, 1
            if direction == 3:
                return 1, 1
            if direction == 5:
                return 1, -1
            if direction == 6:
                return 0, -1
        return 0, 0

    def hex_center(self, r: int, c: int) -> Tuple[float, float]:
        row_step = self.hex_size * math.sqrt(3) + self.spacing
        col_step = self.hex_size * 1.5 + self.spacing
        x_offset = 50
        y_offset = 50
        cx = x_offset + c * col_step
        cy = y_offset + r * row_step + (row_step / 2 if c % 2 else 0)
        return cx, cy

    def hex_side_center(self, r: int, c: int, direction: int) -> Tuple[float, float]:
        """Return the midpoint of the given hex side.

        ``direction`` should be 1-6 with 1=N and increasing clockwise.
        """
        cx, cy = self.hex_center(r, c)
        # Angles for the midpoints of each side in screen coordinates
        angles = {
            1: 270,  # North
            2: 330,  # North-East
            3: 30,   # South-East
            4: 90,   # South
            5: 150,  # South-West
            6: 210,  # North-West
        }
        angle_rad = math.radians(angles.get(direction, 0))
        x = cx + self.hex_size * math.cos(angle_rad)
        y = cy + self.hex_size * math.sin(angle_rad)
        return x, y

    def hex_side_points(
        self, r: int, c: int, direction: int
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Return the endpoint coordinates for a hexagon side.

        ``direction`` should be ``1-6`` with ``1`` at the north side and
        increasing clockwise. The points are ordered counter-clockwise around the
        hexagon.
        """
        cx, cy = self.hex_center(r, c)
        angles = {
            1: (60, 120),
            2: (0, 60),
            3: (300, 0),
            4: (240, 300),
            5: (180, 240),
            6: (120, 180),
        }
        a1, a2 = angles.get(direction, (0, 0))
        x1 = cx + self.hex_size * math.cos(math.radians(a1))
        y1 = cy + self.hex_size * math.sin(math.radians(a1))
        x2 = cx + self.hex_size * math.cos(math.radians(a2))
        y2 = cy + self.hex_size * math.sin(math.radians(a2))
        return (x1, y1), (x2, y2)

    def direction_index(self, r1: int, c1: int, r2: int, c2: int) -> int:
        """Return direction index (1-6) from (r1, c1) to (r2, c2)."""
        cx1, cy1 = self.hex_center(r1, c1)
        cx2, cy2 = self.hex_center(r2, c2)
        angle = math.degrees(math.atan2(cy1 - cy2, cx2 - cx1))
        return int(round(((90 - angle) % 360) / 60)) + 1

    def border_lines_with_ids(
        self,
    ) -> List[Tuple[float, float, float, float, str, int, int, int]]:
        """Return line coordinates with colors and the connected node ids."""
        lines: List[Tuple[float, float, float, float, str, int, int, int]] = []
        drawn_pairs: set[tuple[int, int]] = set()
        nodes_dict = self.world_data.get("nodes", {})
        for r in range(self.rows):
            for c in range(self.cols):
                jid = self.static_grid_occupied[r][c]
                if jid is None:
                    continue
                node = nodes_dict.get(str(jid))
                if not node:
                    continue
                for idx, nb in enumerate(node.get("neighbors", [])):
                    nbid = nb.get("id")
                    if (
                        isinstance(nbid, int)
                        and nbid in self.map_static_positions
                        and idx < MAX_NEIGHBORS
                    ):
                        pair = tuple(sorted((jid, nbid)))
                        if pair in drawn_pairs:
                            continue
                        drawn_pairs.add(pair)

                        if jid <= nbid:
                            start_r, start_c = r, c
                            start_idx = idx + 1
                            end_r, end_c = self.map_static_positions[nbid]
                            end_idx = ((idx + MAX_NEIGHBORS // 2) % MAX_NEIGHBORS) + 1
                        else:
                            other = nodes_dict.get(str(nbid))
                            rev_idx = None
                            if other:
                                for i, ent in enumerate(other.get("neighbors", [])):
                                    if ent.get("id") == jid:
                                        rev_idx = i
                                        break
                            if rev_idx is None:
                                rev_idx = (idx + MAX_NEIGHBORS // 2) % MAX_NEIGHBORS
                            start_r, start_c = self.map_static_positions[nbid]
                            start_idx = rev_idx + 1
                            end_r, end_c = r, c
                            end_idx = ((rev_idx + MAX_NEIGHBORS // 2) % MAX_NEIGHBORS) + 1

                        start_x, start_y = self.hex_side_center(start_r, start_c, start_idx)
                        end_x, end_y = self.hex_side_center(end_r, end_c, end_idx)

                        color = BORDER_COLORS.get(
                            nb.get("border", NEIGHBOR_NONE_STR), "gray"
                        )
                        width = 3 if color in ["black", "brown", "blue"] else 2
                        lines.append(
                            (start_x, start_y, end_x, end_y, color, width, jid, nbid)
                        )
        return lines

    def border_lines(self) -> List[Tuple[float, float, float, float, str, int]]:
        """Return list of lines between neighbors for drawing."""
        return [
            (x1, y1, x2, y2, color, width)
            for x1, y1, x2, y2, color, width, _jid1, _jid2 in self.border_lines_with_ids()
        ]

    def adjacent_hex_pairs(self) -> List[Tuple[int, int, int]]:
        """Return pairs of adjacent nodes on the grid.

        Each tuple contains ``(id1, id2, direction)`` where ``direction`` is the
        side index from ``id1`` to ``id2`` (1-6). Pairs are returned only once
        regardless of order.
        """
        pairs: List[Tuple[int, int, int]] = []
        seen: set[tuple[int, int]] = set()

        for r in range(self.rows):
            for c in range(self.cols):
                nid = self.static_grid_occupied[r][c]
                if nid is None:
                    continue
                for direction in range(1, MAX_NEIGHBORS + 1):
                    dr, dc = self.direction_offset(direction, c)
                    nr, nc = r + dr, c + dc
                    if nr < 0 or nr >= self.rows or nc < 0 or nc >= self.cols:
                        continue
                    other = self.static_grid_occupied[nr][nc]
                    if other is None:
                        continue
                    key = tuple(sorted((nid, other)))
                    if key in seen:
                        continue
                    seen.add(key)
                    pairs.append((nid, other, direction))

        return pairs
