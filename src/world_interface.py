from __future__ import annotations

from abc import ABC, abstractmethod
import json
import os
from typing import Any, Dict, Tuple
from constants import (
    BORDER_TYPES,
    MAX_NEIGHBORS,
    NEIGHBOR_NONE_STR,
    NEIGHBOR_OTHER_STR,
    DAGSVERKEN_LEVELS,
)
from weather import NORMAL_WEATHER


class WorldInterface(ABC):
    """Interface defining operations on world data."""

    def __init__(self, world_data: Dict[str, Any] | None = None) -> None:
        self.world_data = world_data or {}

    def set_world_data(self, world_data: Dict[str, Any]) -> None:
        """Update the reference to the active world data."""
        self.world_data = world_data

    @abstractmethod
    def get_depth_of_node(self, node_id: int) -> int:
        pass

    # -------------------------------------------
    # World data file helpers
    # -------------------------------------------
    @staticmethod
    def load_worlds_file(file_path: str) -> Dict[str, Any]:
        """Load world data from ``file_path``. Returns empty dict on failure."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:  # json.JSONDecodeError or IOError
                print(f"Error loading file {file_path}: {e}")
        return {}

    @staticmethod
    def save_worlds_file(all_worlds: Dict[str, Any], file_path: str) -> None:
        """Save ``all_worlds`` to ``file_path``."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_worlds, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")

    # -------------------------------------------
    # Data validation helpers
    # -------------------------------------------
    def validate_world_data(self) -> Tuple[int, int]:
        """Check ``self.world_data`` for consistency and fix issues.

        Returns a tuple ``(nodes_updated, chars_updated)`` indicating how many
        nodes and characters were modified during validation.
        """
        if "nodes" not in self.world_data:
            self.world_data["nodes"] = {}
        if "characters" not in self.world_data:
            self.world_data["characters"] = {}
        if "next_node_id" not in self.world_data:
            max_id = 0
            for nid_str in self.world_data.get("nodes", {}).keys():
                try:
                    max_id = max(max_id, int(nid_str))
                except ValueError:
                    pass
            self.world_data["next_node_id"] = max_id + 1

        nodes_updated = 0
        chars_updated = 0
        max_node_id_found = 0
        all_node_ids: set[int] = set()

        for nid_str, node in list(self.world_data.get("nodes", {}).items()):
            try:
                nid_int = int(nid_str)
            except ValueError:
                print(f"Skipping node with non-integer key: {nid_str}")
                del self.world_data["nodes"][nid_str]
                continue

            all_node_ids.add(nid_int)
            max_node_id_found = max(max_node_id_found, nid_int)

            updated = False
            if "node_id" not in node:
                node["node_id"] = nid_int
                updated = True
            if "parent_id" not in node:
                node["parent_id"] = None
            if "name" not in node:
                node["name"] = ""
                updated = True
            if "custom_name" not in node:
                node["custom_name"] = ""
                updated = True
            if "ruler_id" not in node:
                node["ruler_id"] = None
            if "num_subfiefs" not in node:
                node["num_subfiefs"] = 0
                updated = True
            if "children" not in node:
                node["children"] = []
                updated = True
            res_type = node.get("res_type")
            if res_type == "Vildmark":
                if "tunnland" not in node:
                    node["tunnland"] = 0
                    updated = True
            elif res_type == "Jaktmark":
                if "tunnland" not in node:
                    node["tunnland"] = 0
                    updated = True
                if "hunters" not in node:
                    node["hunters"] = 0
                    updated = True
                if "gamekeeper_id" not in node:
                    node["gamekeeper_id"] = None
                    updated = True
            elif res_type == "Mark":
                for key in ("total_land", "forest_land", "cleared_land"):
                    if key not in node:
                        node[key] = 0
                        updated = True
            elif res_type == "Djur":
                if "population" in node:
                    del node["population"]
                    updated = True
            else:
                if "population" not in node:
                    node["population"] = 0
                    updated = True

            node["children"] = [int(c) for c in node.get("children", []) if str(c).isdigit()]

            depth = self.get_depth_of_node(nid_int)
            if depth == 3:
                if "neighbors" not in node:
                    node["neighbors"] = [
                        {"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)
                    ]
                    updated = True
                else:
                    neighbors = node["neighbors"]
                    if not isinstance(neighbors, list):
                        neighbors = []
                    validated_neighbors = []
                    for i in range(MAX_NEIGHBORS):
                        if i < len(neighbors) and isinstance(neighbors[i], dict):
                            n_data = neighbors[i]
                            n_id = n_data.get("id")
                            n_border = n_data.get("border", NEIGHBOR_NONE_STR)
                            final_id = None
                            if isinstance(n_id, int):
                                final_id = n_id
                            elif str(n_id).isdigit():
                                final_id = int(n_id)
                            elif n_id == NEIGHBOR_OTHER_STR:
                                final_id = NEIGHBOR_OTHER_STR
                            if n_border not in BORDER_TYPES:
                                n_border = NEIGHBOR_NONE_STR
                            validated_neighbors.append({"id": final_id, "border": n_border})
                        else:
                            validated_neighbors.append({"id": None, "border": NEIGHBOR_NONE_STR})
                    if node.get("neighbors") != validated_neighbors:
                        node["neighbors"] = validated_neighbors
                        updated = True
                if "dagsverken" not in node or node["dagsverken"] not in DAGSVERKEN_LEVELS:
                    node["dagsverken"] = "normalt"
                    updated = True
                for key in (
                    "work_available",
                    "work_needed",
                    "storage_silver",
                    "storage_basic",
                    "storage_luxury",
                    "jarldom_area",
                    "expected_license_income",
                ):
                    if key not in node:
                        node[key] = 0
                        updated = True
            elif depth >= 4:
                if "res_type" not in node:
                    node["res_type"] = "Resurs"
                    updated = True
                res_type = node.get("res_type")
                # Soldiers field only for Soldier resources
                if res_type == "Soldater":
                    if "soldiers" not in node or not isinstance(node["soldiers"], list):
                        node["soldiers"] = []
                        updated = True
                else:
                    if "soldiers" in node:
                        del node["soldiers"]
                        updated = True

                # Animals field only for Animal resources
                if res_type == "Djur":
                    if "animals" not in node or not isinstance(node["animals"], list):
                        node["animals"] = []
                        updated = True
                else:
                    if "animals" in node:
                        del node["animals"]
                        updated = True

                # Land fields only for Mark resources
                if res_type == "Mark":
                    for key in ("total_land", "forest_land", "cleared_land"):
                        if key not in node:
                            node[key] = 0
                            updated = True
                elif res_type == "Gods":
                    defaults = {
                        "manor_land": 0,
                        "cultivated_land": 0,
                        "cultivated_quality": 3,
                        "fallow_land": 0,
                        "has_herd": False,
                        "forest_land": 0,
                        "hunt_quality": 3,
                        "hunting_law": 0,
                    }
                    for key, val in defaults.items():
                        if key not in node:
                            node[key] = val
                            updated = True
                    try:
                        cq = int(node.get("cultivated_quality", 3))
                    except (ValueError, TypeError):
                        cq = 3
                    cq = max(1, min(cq, 5))
                    if node.get("cultivated_quality") != cq:
                        node["cultivated_quality"] = cq
                        updated = True
                    try:
                        hq = int(node.get("hunt_quality", 3))
                    except (ValueError, TypeError):
                        hq = 3
                    hq = max(1, min(hq, 5))
                    if node.get("hunt_quality") != hq:
                        node["hunt_quality"] = hq
                        updated = True
                    try:
                        hl = int(node.get("hunting_law", 0))
                    except (ValueError, TypeError):
                        hl = 0
                    hl = max(0, min(hl, 20))
                    if node.get("hunting_law") != hl:
                        node["hunting_law"] = hl
                        updated = True
                elif res_type == "Djur":
                    if "population" in node:
                        del node["population"]
                        updated = True
                elif res_type in {"Hav", "Flod"}:
                    if "fish_quality" not in node:
                        node["fish_quality"] = "Normalt"
                        updated = True
                    if "fishing_boats" not in node:
                        node["fishing_boats"] = 0
                        updated = True
                    if res_type == "Flod":
                        if "river_level" not in node:
                            node["river_level"] = 1
                            updated = True
                    elif "river_level" in node:
                        del node["river_level"]
                        updated = True
                elif res_type == "Lager":
                    defaults = {
                        "lager_text": "",
                        "storage_silver": 0,
                        "storage_basic": 0,
                        "storage_luxury": 0,
                        "storage_timber": 0,
                        "storage_coal": 0,
                        "storage_iron_ore": 0,
                        "storage_iron": 0,
                        "storage_animal_feed": 0,
                        "storage_skin": 0,
                    }
                    for key, val in defaults.items():
                        if key not in node:
                            node[key] = val
                            updated = True
                    for key in (
                        "population",
                        "tunnland",
                        "hunters",
                        "gamekeeper_id",
                        "animals",
                        "soldiers",
                        "total_land",
                        "forest_land",
                        "cleared_land",
                        "manor_land",
                        "cultivated_land",
                        "cultivated_quality",
                        "fallow_land",
                        "has_herd",
                        "hunt_quality",
                        "hunting_law",
                        "fish_quality",
                        "fishing_boats",
                        "river_level",
                    ):
                        if key in node:
                            del node[key]
                            updated = True
                elif res_type == "Jaktmark":
                    if "tunnland" not in node:
                        node["tunnland"] = 0
                        updated = True
                    if "hunters" not in node:
                        node["hunters"] = 0
                        updated = True
                    if "gamekeeper_id" not in node:
                        node["gamekeeper_id"] = None
                        updated = True
                elif res_type == "Väder":
                    defaults = {
                        "spring_weather": NORMAL_WEATHER["spring"],
                        "summer_weather": NORMAL_WEATHER["summer"],
                        "autumn_weather": NORMAL_WEATHER["autumn"],
                        "winter_weather": NORMAL_WEATHER["winter"],
                        "weather_effect": "",
                    }
                    for key, val in defaults.items():
                        if key not in node:
                            node[key] = val
                            updated = True
                    for key in (
                        "population",
                        "tunnland",
                        "hunters",
                        "gamekeeper_id",
                        "animals",
                        "soldiers",
                        "total_land",
                        "forest_land",
                        "cleared_land",
                        "manor_land",
                        "cultivated_land",
                        "cultivated_quality",
                        "fallow_land",
                        "has_herd",
                        "hunt_quality",
                        "hunting_law",
                        "fish_quality",
                        "fishing_boats",
                        "river_level",
                    ):
                        if key in node:
                            del node[key]
                            updated = True
                else:
                    for key in (
                        "total_land",
                        "forest_land",
                        "cleared_land",
                        "manor_land",
                        "cultivated_land",
                        "cultivated_quality",
                        "fallow_land",
                        "has_herd",
                        "hunt_quality",
                        "hunting_law",
                    ):
                        if key in node:
                            del node[key]
                            updated = True

                for key in ("characters", "buildings"):
                    if key not in node or not isinstance(node[key], list):
                        node[key] = []
                        updated = True

            if updated:
                nodes_updated += 1

        for nid_str, node in self.world_data.get("nodes", {}).items():
            nid_int = int(nid_str)
            parent_id = node.get("parent_id")
            if parent_id is not None and parent_id not in all_node_ids:
                print(
                    f"Warning: Node {nid_int} has invalid parent_id {parent_id}. Setting parent to None."
                )
                node["parent_id"] = None
                nodes_updated += 1
            valid_children = []
            for child_id in node.get("children", []):
                if child_id in all_node_ids:
                    child_node = self.world_data["nodes"].get(str(child_id))
                    if child_node:
                        if child_node.get("parent_id") != nid_int:
                            print(
                                f"Warning: Child {child_id} parent_id ({child_node.get('parent_id')}) doesn't match parent {nid_int}. Fixing child."
                            )
                            child_node["parent_id"] = nid_int
                            nodes_updated += 1
                        valid_children.append(child_id)
                    else:
                        print(
                            f"Error: Child node {child_id} found in ID set but not in dictionary."
                        )
                else:
                    print(
                        f"Warning: Node {nid_int} has invalid child_id {child_id}. Removing child link."
                    )
                    nodes_updated += 1
            if node.get("children", []) != valid_children:
                node["children"] = valid_children

        for cid_str, char in self.world_data.get("characters", {}).items():
            updated = False
            if "char_id" not in char:
                char["char_id"] = int(cid_str)
                updated = True
            if "name" not in char:
                char["name"] = ""
                updated = True
            if "wealth" not in char:
                char["wealth"] = 0
                updated = True
            if "description" not in char:
                char["description"] = ""
                updated = True
            if "skills" not in char:
                char["skills"] = []
                updated = True
            if "type" not in char:
                char["type"] = ""
                updated = True
            if "ruler_of" not in char:
                char["ruler_of"] = None
                updated = True
            if updated:
                chars_updated += 1

        valid_char_ids = set(self.world_data.get("characters", {}).keys())
        for node in self.world_data.get("nodes", {}).values():
            ruler_id = node.get("ruler_id")
            if ruler_id is not None and str(ruler_id) not in valid_char_ids:
                print(
                    f"Warning: Node {node.get('node_id','??')} has invalid ruler_id {ruler_id}. Clearing ruler."
                )
                node["ruler_id"] = None
                nodes_updated += 1

        calculated_next_id = max(max_node_id_found, 0) + 1
        if self.world_data.get("next_node_id", 1) < calculated_next_id:
            print(
                f"Warning: World next_node_id ({self.world_data.get('next_node_id', 1)}) was lower than max found ID ({max_node_id_found}). Updating."
            )
            self.world_data["next_node_id"] = calculated_next_id
            nodes_updated += 1

        return nodes_updated, chars_updated

    @abstractmethod
    def get_display_name_for_node(self, node_data: Dict[str, Any] | Any, depth: int) -> str:
        pass

    @abstractmethod
    def update_subfiefs_for_node(self, node_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def delete_node_and_descendants(self, node_id: int) -> int:
        pass

    @abstractmethod
    def attempt_link_neighbors(self, node_id1: int, node_id2: int) -> tuple[bool, str]:
        """Link two jarldoms. Returns success flag and status message."""
        pass
