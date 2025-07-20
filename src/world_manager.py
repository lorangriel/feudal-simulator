from __future__ import annotations

import copy
import math
from typing import Any, Dict, List

from utils import generate_swedish_village_name
from constants import MAX_NEIGHBORS, NEIGHBOR_NONE_STR
from node import Node
from world_interface import WorldInterface


class WorldManager(WorldInterface):
    """Implementation of ``WorldInterface`` with basic world logic."""

    def __init__(self, world_data: Dict[str, Any] | None = None) -> None:
        super().__init__(world_data)
        self._depth_cache: Dict[int, int] = {}

    # -------------------------------------------
    # Utility methods
    # -------------------------------------------
    def clear_depth_cache(self) -> None:
        self._depth_cache = {}

    # -------------------------------------------
    # WorldInterface implementation
    # -------------------------------------------
    def get_depth_of_node(self, node_id: int) -> int:
        """Calculates the depth of ``node_id`` in the hierarchy."""
        if node_id in self._depth_cache:
            return self._depth_cache[node_id]

        nodes_dict = self.world_data.get("nodes", {})
        depth = 0
        current_node_id = node_id
        visited = {current_node_id}

        while True:
            current_node_data = nodes_dict.get(str(current_node_id))
            if not current_node_data:
                self._depth_cache[node_id] = -1
                return -1
            parent_id = current_node_data.get("parent_id")
            if parent_id is None:
                self._depth_cache[node_id] = depth
                return depth
            if str(parent_id) not in nodes_dict:
                self._depth_cache[node_id] = depth
                return depth
            depth += 1
            current_node_id = parent_id
            if current_node_id in visited:
                self._depth_cache[node_id] = -99
                return -99
            visited.add(current_node_id)
            if depth > 50:
                self._depth_cache[node_id] = -100
                return -100

    def get_display_name_for_node(self, node_data: Dict[str, Any] | Any, depth: int) -> str:
        """Return a readable name for ``node_data`` at ``depth``."""
        if isinstance(node_data, Node):
            node_id = node_data.node_id
            name = node_data.name
            custom_name = node_data.custom_name.strip()
            res_type = node_data.res_type
            ruler_id = node_data.ruler_id
        else:
            node_id = node_data.get("node_id", "??")
            name = node_data.get("name", "")
            custom_name = node_data.get("custom_name", "").strip()
            res_type = node_data.get("res_type", "")
            ruler_id = node_data.get("ruler_id")

        level_name = ""
        show_id = True
        if depth == 0:
            level_name = name or "Kungarike"
        elif depth == 1:
            level_name = name or "Furstendöme"
        elif depth == 2:
            level_name = name or "Hertigdöme"
        elif depth == 3:
            return f"{custom_name or f'Jarldöme {node_id}'} (ägande nod)"
        else:
            ruler_str = ""
            if ruler_id and "characters" in self.world_data:
                ruler_data = self.world_data["characters"].get(str(ruler_id))
                if ruler_data:
                    ruler_str = ruler_data.get("name", f"Härskare {ruler_id}")
            parts: List[str] = []
            if res_type and res_type != "Resurs":
                parts.append(res_type)
            if custom_name:
                parts.append(custom_name)
            if ruler_str:
                parts.append(f"({ruler_str})")
            if not parts:
                return f"Resurs {node_id} (ägande nod)"
            return " - ".join(parts) + " (ägande nod)"

        display = level_name
        if custom_name and custom_name != level_name:
            display += f" [{custom_name}]"
        if show_id:
            display += f" (ID: {node_id})"
        display += " (ägande nod)"
        return display

    def update_subfiefs_for_node(self, node_data: Dict[str, Any]) -> None:
        current_children_ids = set(node_data.get("children", []))
        target_count = node_data.get("num_subfiefs", 0)
        depth = self.get_depth_of_node(node_data["node_id"])

        while len(current_children_ids) < target_count:
            self.world_data["next_node_id"] += 1
            new_id = self.world_data["next_node_id"]
            new_id_str = str(new_id)

            if depth == 0:
                child_name = "Furstendöme"
            elif depth == 1:
                child_name = "Hertigdöme"
            elif depth == 2:
                child_name = "Resurs"
            elif depth == 3:
                child_name = "Resurs"
            else:
                child_name = "Nod"

            new_node: Dict[str, Any] = {
                "node_id": new_id,
                "parent_id": node_data["node_id"],
                "name": child_name,
                "children": [],
                "num_subfiefs": 0,
                "ruler_id": None,
            }
            if depth == 2:
                new_node["res_type"] = "Resurs"
                new_node["custom_name"] = generate_swedish_village_name()
            elif depth >= 3:
                new_node["res_type"] = "Resurs"
                new_node["custom_name"] = ""

            self.world_data["nodes"][new_id_str] = new_node
            node_data.setdefault("children", []).append(new_id)
            current_children_ids.add(new_id)

        children_to_remove = list(current_children_ids)
        while len(children_to_remove) > target_count:
            child_id_to_remove = children_to_remove.pop()
            if child_id_to_remove in node_data.get("children", []):
                node_data["children"].remove(child_id_to_remove)
            self.delete_node_and_descendants(child_id_to_remove)

    def delete_node_and_descendants(self, node_id: int) -> int:
        node_id_str = str(node_id)
        if node_id_str not in self.world_data.get("nodes", {}):
            return 0
        deleted_count = 1
        node_to_delete = self.world_data["nodes"][node_id_str]
        for child_id in list(node_to_delete.get("children", [])):
            deleted_count += self.delete_node_and_descendants(child_id)
        parent_id = node_to_delete.get("parent_id")
        if parent_id is not None:
            parent_node = self.world_data["nodes"].get(str(parent_id))
            if parent_node and "children" in parent_node:
                if node_id in parent_node["children"]:
                    parent_node["children"].remove(node_id)
                elif str(node_id) in parent_node["children"]:
                    parent_node["children"].remove(str(node_id))
        if node_id_str in self.world_data["nodes"]:
            del self.world_data["nodes"][node_id_str]
        return deleted_count

    def attempt_link_neighbors(self, node_id1: int, node_id2: int) -> tuple[bool, str]:
        node1 = self.world_data["nodes"].get(str(node_id1))
        node2 = self.world_data["nodes"].get(str(node_id2))
        if not node1 or not node2:
            return False, "Fel: En eller båda noder kunde inte hittas."
        if self.get_depth_of_node(node_id1) != 3 or self.get_depth_of_node(node_id2) != 3:
            return False, "Fel: Kan bara länka Jarldömen (nivå 3)."
        neighbors1 = node1.get("neighbors", [])
        neighbors2 = node2.get("neighbors", [])
        if any(nb.get("id") == node_id2 for nb in neighbors1) or any(nb.get("id") == node_id1 for nb in neighbors2):
            msg = f"Fel: {node1.get('custom_name', f'ID:{node_id1}')} och {node2.get('custom_name', f'ID:{node_id2}')} är redan grannar."
            return False, msg
        free_slots1 = sum(1 for nb in neighbors1 if nb.get("id") is None)
        free_slots2 = sum(1 for nb in neighbors2 if nb.get("id") is None)
        if free_slots1 > 0 and free_slots2 > 0:
            for i, nb in enumerate(neighbors1):
                if nb.get("id") is None:
                    neighbors1[i]["id"] = node_id2
                    neighbors1[i]["border"] = NEIGHBOR_NONE_STR
                    break
            for i, nb in enumerate(neighbors2):
                if nb.get("id") is None:
                    neighbors2[i]["id"] = node_id1
                    neighbors2[i]["border"] = NEIGHBOR_NONE_STR
                    break
            node1["neighbors"] = neighbors1
            node2["neighbors"] = neighbors2
            msg = f"{node1.get('custom_name', f'ID:{node_id1}')} och {node2.get('custom_name', f'ID:{node_id2}')} är nu grannar."
            return True, msg
        else:
            reason = ""
            if free_slots1 == 0 and free_slots2 == 0:
                reason = "Båda jarldömmena har maximalt antal grannar."
            elif free_slots1 == 0:
                reason = f"{node1.get('custom_name', f'ID:{node_id1}')} har maximalt antal grannar."
            elif free_slots2 == 0:
                reason = f"{node2.get('custom_name', f'ID:{node_id2}')} har maximalt antal grannar."
            return False, f"Fel: Kunde inte länka grannar. {reason}"

    # -------------------------------------------
    # Bidirectional neighbor management
    # -------------------------------------------
    def update_neighbors_for_node(self, node_id: int, new_neighbors: List[Dict[str, Any]]) -> None:
        """Replace ``node_id`` neighbor list with ``new_neighbors`` and ensure
        links are bidirectional."""

        node = self.world_data.get("nodes", {}).get(str(node_id))
        if not node:
            return

        # Ensure neighbor lists have the expected length
        old_neighbors = node.get("neighbors", [])
        if len(old_neighbors) < MAX_NEIGHBORS:
            old_neighbors.extend(
                {"id": None, "border": NEIGHBOR_NONE_STR}
                for _ in range(MAX_NEIGHBORS - len(old_neighbors))
            )
            node["neighbors"] = old_neighbors
        if len(new_neighbors) < MAX_NEIGHBORS:
            new_neighbors = new_neighbors + [
                {"id": None, "border": NEIGHBOR_NONE_STR}
                for _ in range(MAX_NEIGHBORS - len(new_neighbors))
            ]
        old_ids = {
            nb.get("id")
            for nb in old_neighbors
            if isinstance(nb, dict) and isinstance(nb.get("id"), int)
        }
        new_ids = {
            nb.get("id")
            for nb in new_neighbors
            if isinstance(nb, dict) and isinstance(nb.get("id"), int)
        }

        nodes_dict = self.world_data.get("nodes", {})

        # Remove stale links from neighbors no longer referenced
        for rid in old_ids - new_ids:
            other = nodes_dict.get(str(rid))
            if not other:
                continue
            other_neighbors = other.get("neighbors", [])
            if len(other_neighbors) < MAX_NEIGHBORS:
                other_neighbors.extend(
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - len(other_neighbors))
                )
                other["neighbors"] = other_neighbors
            for nb in other_neighbors:
                if nb.get("id") == node_id:
                    nb["id"] = None
                    nb["border"] = NEIGHBOR_NONE_STR
                    break

        # Add/update reverse links for each new neighbor
        for entry in new_neighbors:
            nid = entry.get("id")
            if not isinstance(nid, int):
                continue
            other = nodes_dict.get(str(nid))
            if not other:
                continue
            border_val = entry.get("border", NEIGHBOR_NONE_STR)
            link_found = False
            other_neighbors = other.get("neighbors", [])
            if len(other_neighbors) < MAX_NEIGHBORS:
                other_neighbors.extend(
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - len(other_neighbors))
                )
                other["neighbors"] = other_neighbors
            for nb in other_neighbors:
                if nb.get("id") == node_id:
                    nb["border"] = border_val
                    link_found = True
                    break
            if not link_found:
                for nb in other_neighbors:
                    if nb.get("id") is None:
                        nb["id"] = node_id
                        nb["border"] = border_val
                        link_found = True
                        break

        node["neighbors"] = new_neighbors
