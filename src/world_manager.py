from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from events import PROVINCE_OWNER_CHANGED
from utils import generate_swedish_village_name
from constants import (
    MAX_NEIGHBORS,
    NEIGHBOR_NONE_STR,
    BORDER_TYPES,
    DAGSVERKEN_MULTIPLIERS,
    DAGSVERKEN_UMBARANDE,
    THRALL_WORK_DAYS,
    DAY_LABORER_WORK_DAYS,
    CRAFTSMAN_LICENSE_FEES,
)
from node import Node
from personal_province import (
    PersonalProvinceError,
    build_personal_path,
    validate_assignment,
)
from world_interface import WorldInterface


@dataclass
class AssignResult:
    success: bool
    message: str = ""
    owner_level: str | None = None
    owner_id: int | None = None
    personal_path: list[int] | None = None
    changed: bool = False


class WorldManager(WorldInterface):
    """Implementation of ``WorldInterface`` with basic world logic."""

    def __init__(
        self, world_data: Dict[str, Any] | None = None, event_bus=None
    ) -> None:
        super().__init__(world_data)
        self._depth_cache: Dict[int, int] = {}
        self._snapshots: list[dict[str, Any]] = []
        self._tax_cache_stale = False
        self._event_bus = event_bus

    # -------------------------------------------
    # Utility methods
    # -------------------------------------------
    def clear_depth_cache(self) -> None:
        self._depth_cache = {}

    def set_event_bus(self, event_bus) -> None:
        self._event_bus = event_bus

    def create_snapshot(self, reason: str = "", context: Dict[str, Any] | None = None) -> None:
        """Store a lightweight copy of the world for undo/inspection."""

        snapshot = {
            "reason": reason,
            "context": context or {},
            "state": copy.deepcopy(self.world_data),
        }
        self._snapshots.append(snapshot)

    def _lineage_for_node(self, node_id: int) -> List[int]:
        nodes = self.world_data.get("nodes", {})
        lineage: List[int] = []
        current = node_id
        while True:
            node = nodes.get(str(current))
            if not node:
                break
            parent_raw = node.get("parent_id")
            if isinstance(parent_raw, str) and parent_raw.isdigit():
                parent_id = int(parent_raw)
            else:
                parent_id = parent_raw
            if parent_id is None:
                break
            lineage.insert(0, parent_id)
            current = parent_id
        return lineage

    def _is_descendant(self, ancestor_id: int, candidate_id: int) -> bool:
        nodes = self.world_data.get("nodes", {})
        stack = [ancestor_id]
        visited: set[int] = set()
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            if current == candidate_id and current != ancestor_id:
                return True
            node = nodes.get(str(current))
            if not node:
                continue
            for child in node.get("children", []):
                try:
                    stack.append(int(child))
                except (TypeError, ValueError):
                    continue
        return False

    def _recalculate_personal_economy(self, node_id: int) -> None:
        """Mark caches dirty and recompute simple income placeholders."""

        self._tax_cache_stale = True
        try:
            self.calculate_license_income(node_id)
        except Exception:
            pass

    def _emit_owner_change_event(self, province_id: int, owner_id: int | None) -> None:
        if not self._event_bus:
            return

        emit_fn = getattr(self._event_bus, "emit", None)
        if callable(emit_fn):
            emit_fn(
                PROVINCE_OWNER_CHANGED,
                province_id=province_id,
                new_owner_id=owner_id,
            )

    def assign_personal_owner(
        self, province_id: int | str, owner_anchor_id: Tuple[str, int | None] | str | None
    ) -> AssignResult:
        """Validate and assign a personal owner for ``province_id``.

        ``owner_anchor_id`` is expected to be a tuple of (level, owner_id) but
        falls back to sensible defaults for backwards compatibility.
        """

        try:
            province_int = int(province_id)
        except (TypeError, ValueError):
            return AssignResult(False, "Ogiltigt provins-id")

        nodes = self.world_data.get("nodes", {})
        node_data = nodes.get(str(province_int))
        if not node_data:
            return AssignResult(False, "Provinsen kunde inte hittas")

        owner_level: str
        owner_id: Optional[int]
        if isinstance(owner_anchor_id, tuple) and len(owner_anchor_id) == 2:
            owner_level, owner_id = owner_anchor_id
        elif owner_anchor_id in (None, "none"):
            owner_level, owner_id = "none", None
        else:
            owner_level = "0"
            try:
                owner_id = int(owner_anchor_id) if owner_anchor_id is not None else None
            except (TypeError, ValueError):
                owner_id = None

        owner_level = str(owner_level or "none")
        current_level = str(node_data.get("owner_assigned_level", "none") or "none")
        current_owner = node_data.get("owner_assigned_id")

        if owner_level == current_level and owner_id == current_owner:
            return AssignResult(
                True,
                "Ingen ändring",
                owner_level=current_level,
                owner_id=current_owner,
                personal_path=list(node_data.get("personal_province_path", [])),
                changed=False,
            )

        try:
            validate_assignment(owner_level, owner_id, current_owner)
        except PersonalProvinceError as exc:
            return AssignResult(False, str(exc))

        if owner_level != "none":
            if owner_id is None or str(owner_id) not in nodes:
                return AssignResult(False, "Ägaren finns inte i världen")
            owner_depth = self.get_depth_of_node(owner_id)
            try:
                expected_depth = int(owner_level)
            except ValueError:
                expected_depth = -1
            if owner_depth != expected_depth:
                return AssignResult(False, "Ogiltig ankarnivå för vald ägare")
            if owner_id == province_int or self._is_descendant(province_int, owner_id):
                return AssignResult(False, "Cykel i ägarhierarkin")

        lineage = self._lineage_for_node(province_int)
        try:
            personal_path = build_personal_path(owner_level, owner_id, lineage)
        except PersonalProvinceError as exc:
            return AssignResult(False, str(exc))

        node_data["owner_assigned_level"] = owner_level
        node_data["owner_assigned_id"] = owner_id
        node_data["personal_province_path"] = personal_path

        self._recalculate_personal_economy(province_int)
        self.create_snapshot(
            reason="owner-change",
            context={"province_id": province_int, "owner_id": owner_id},
        )
        self._emit_owner_change_event(province_int, owner_id)

        return AssignResult(
            True,
            "Ägare uppdaterad",
            owner_level=owner_level,
            owner_id=owner_id,
            personal_path=personal_path,
            changed=True,
        )

    @staticmethod
    def calculate_population_from_fields(data: Dict[str, Any]) -> int:
        """Compute total population from category fields."""
        try:
            free_p = int(data.get("free_peasants", 0) or 0)
            unfree_p = int(data.get("unfree_peasants", 0) or 0)
            thralls = int(data.get("thralls", 0) or 0)
            burghers = int(data.get("burghers", 0) or 0)
        except (ValueError, TypeError):
            free_p = unfree_p = thralls = burghers = 0
        total = free_p + unfree_p + thralls + burghers
        if total:
            return total
        try:
            return int(data.get("population", 0) or 0)
        except (ValueError, TypeError):
            return 0

    def update_population_totals(self) -> None:
        """Update population for each node by summing immediate children."""
        nodes = self.world_data.get("nodes", {})
        if not nodes:
            return

        depth_map: Dict[int, int] = {}
        max_depth = 0
        for nid_str in nodes.keys():
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            d = self.get_depth_of_node(nid)
            depth_map[nid] = d
            max_depth = max(max_depth, d)

        base_population: Dict[int, int] = {}
        # Determine the intrinsic population for each node. Always recompute the
        # base value so that changes to settlement fields are reflected on
        # subsequent calls. Use the previously stored ``_base_population`` as the
        # population field to avoid compounding child totals from earlier runs.
        for nid in depth_map:
            node = nodes.get(str(nid))
            if not node:
                continue
            base_input = dict(node)
            if "_base_population" in node:
                base_input["population"] = node["_base_population"]
            base_pop = self.calculate_population_from_fields(base_input)
            node["_base_population"] = base_pop
            base_population[nid] = base_pop

        # Reset all nodes to their base population
        for nid, base_pop in base_population.items():
            nodes[str(nid)]["population"] = base_pop

        # Now accumulate child populations from deepest level upwards
        parent_lookup: Dict[int, List[int]] = {}
        for cid_str, cdata in nodes.items():
            try:
                cid = int(cid_str)
            except ValueError:
                continue
            pid = cdata.get("parent_id")
            if isinstance(pid, str) and pid.isdigit():
                pid = int(pid)
            if isinstance(pid, int):
                parent_lookup.setdefault(pid, []).append(cid)

        for depth in range(max_depth, -1, -1):
            for nid, d in depth_map.items():
                if d != depth:
                    continue
                node = nodes.get(str(nid))
                if not node:
                    continue
                total = base_population.get(nid, 0)
                child_ids = set(node.get("children", []))
                child_ids.update(parent_lookup.get(nid, []))
                for cid in child_ids:
                    child = nodes.get(str(cid))
                    if not child:
                        continue
                    try:
                        total += int(child.get("population", 0) or 0)
                    except (ValueError, TypeError):
                        continue
                node["population"] = total

    def aggregate_resources(self, node_id: int) -> Dict[str, Dict[str, int]]:
        """Return aggregated resource counts for ``node_id`` and descendants."""

        totals = {"soldiers": {}, "characters": {}, "animals": {}, "buildings": {}}
        nodes = self.world_data.get("nodes", {})

        def add_count(target: Dict[str, int], key: str, amount: int = 1) -> None:
            if not key:
                return
            target[key] = target.get(key, 0) + amount

        def recurse(nid: int) -> None:
            node = nodes.get(str(nid))
            if not node:
                return
            for entry in node.get("soldiers", []):
                t = entry.get("type")
                c = entry.get("count", 0)
                try:
                    c = int(c)
                except (ValueError, TypeError):
                    c = 0
                add_count(totals["soldiers"], t, c)
            for entry in node.get("characters", []):
                t = entry.get("type")
                add_count(totals["characters"], t, 1)
            for entry in node.get("animals", []):
                t = entry.get("type")
                c = entry.get("count", 0)
                try:
                    c = int(c)
                except (ValueError, TypeError):
                    c = 0
                add_count(totals["animals"], t, c)
            for entry in node.get("buildings", []):
                t = entry.get("type")
                c = entry.get("count", 0)
                try:
                    c = int(c)
                except (ValueError, TypeError):
                    c = 0
                add_count(totals["buildings"], t, c)

            for child in node.get("children", []):
                recurse(child)

        recurse(node_id)
        return totals

    def calculate_work_available(
        self, node_id: int, visited: set[int] | None = None
    ) -> int:
        """Sum available work days for ``node_id`` and all descendants."""

        nodes = self.world_data.get("nodes", {})
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        node = nodes.get(str(node_id))
        if not node:
            return 0
        try:
            thralls = int(node.get("thralls", 0) or 0)
        except (ValueError, TypeError):
            thralls = 0
        try:
            unfree = int(node.get("unfree_peasants", 0) or 0)
        except (ValueError, TypeError):
            unfree = 0
        try:
            day_laborers = int(node.get("day_laborers_hired", 0) or 0)
        except (ValueError, TypeError):
            day_laborers = 0
        level = node.get("dagsverken", "normalt")
        multiplier = DAGSVERKEN_MULTIPLIERS.get(level, 0)
        total = (
            thralls * THRALL_WORK_DAYS
            + unfree * multiplier
            + day_laborers * DAY_LABORER_WORK_DAYS
        )
        for child in node.get("children", []):
            try:
                cid = int(child)
            except (ValueError, TypeError):
                continue
            total += self.calculate_work_available(cid, visited)
        return total

    def calculate_work_needed(
        self, node_id: int, visited: set[int] | None = None
    ) -> int:
        """Sum required work days for ``node_id`` and its descendants.

        For water resources (``Hav`` or ``Flod``), the required work is
        determined by the number of fishing boats. Each boat requires
        ``THRALL_WORK_DAYS`` work days. For all other resources, the value is
        read directly from the node's ``work_needed`` field.
        """

        nodes = self.world_data.get("nodes", {})
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        node = nodes.get(str(node_id))
        if not node:
            return 0

        res_type = node.get("res_type")
        if res_type in {"Hav", "Flod"}:
            try:
                boats = int(node.get("fishing_boats", 0) or 0)
            except (ValueError, TypeError):
                boats = 0
            total = boats * THRALL_WORK_DAYS
        else:
            try:
                total = int(node.get("work_needed", 0) or 0)
            except (ValueError, TypeError):
                total = 0

        for child in node.get("children", []):
            try:
                cid = int(child)
            except (ValueError, TypeError):
                continue
            total += self.calculate_work_needed(cid, visited)

        return total

    def update_work_needed(self, jarldom_id: int) -> int:
        """Recalculate and store ``work_needed`` for a jarldom.

        ``calculate_work_needed`` sums the requirement for the jarldom and
        all descendant resource nodes.  This helper simply stores that sum on
        the jarldom's node and returns the total for convenience.
        """

        total = self.calculate_work_needed(jarldom_id)
        node = self.world_data.get("nodes", {}).get(str(jarldom_id))
        if node is not None:
            node["work_needed"] = total
        return total

    def calculate_umbarande(self, node_id: int, visited: set[int] | None = None) -> int:
        """Sum umbäranden for ``node_id`` and all descendants.

        Includes both dagsverken and weather modifiers stored on the node.
        """

        nodes = self.world_data.get("nodes", {})
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        node = nodes.get(str(node_id))
        if not node:
            return 0
        level = node.get("dagsverken", "normalt")
        total = DAGSVERKEN_UMBARANDE.get(level, 0)
        try:
            total += int(node.get("weather_effect", 0) or 0)
        except (ValueError, TypeError):
            pass
        for child in node.get("children", []):
            try:
                cid = int(child)
            except (ValueError, TypeError):
                continue
            total += self.calculate_umbarande(cid, visited)
        return total

    def calculate_license_income(
        self, node_id: int, visited: set[int] | None = None
    ) -> int:
        """Sum expected license income for ``node_id`` and all descendants."""

        nodes = self.world_data.get("nodes", {})
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        node = nodes.get(str(node_id))
        if not node:
            return 0
        try:
            total = int(node.get("expected_license_income", 0) or 0)
        except (ValueError, TypeError):
            total = 0
        for child in node.get("children", []):
            try:
                cid = int(child)
            except (ValueError, TypeError):
                continue
            total += self.calculate_license_income(cid, visited)
        return total

    def _calculate_craftsman_license(self, node_id: int) -> int:
        """Recursively calculate license fees from craftsmen for ``node_id``."""

        nodes = self.world_data.get("nodes", {})
        node = nodes.get(str(node_id))
        if not node:
            return 0

        total = 0
        for c in node.get("craftsmen", []):
            ctype = c.get("type")
            try:
                count = int(c.get("count", 0) or 0)
            except (ValueError, TypeError):
                count = 0
            fee = CRAFTSMAN_LICENSE_FEES.get(ctype, 0)
            total += fee * count

        for child in node.get("children", []):
            try:
                cid = int(child)
            except (ValueError, TypeError):
                continue
            total += self._calculate_craftsman_license(cid)
        return total

    def update_license_income(self, jarldom_id: int) -> int:
        """Update ``expected_license_income`` for a jarldom from craftsmen."""

        total = self._calculate_craftsman_license(jarldom_id)
        node = self.world_data.get("nodes", {}).get(str(jarldom_id))
        if node is not None:
            node["expected_license_income"] = total
        return total

    def calculate_total_resources(
        self,
        node_id: int,
        visited: set[int] | None = None,
        parent_lookup: Dict[int, List[int]] | None = None,
    ) -> Dict[str, Any]:
        """Recursively sum resources for ``node_id`` and store on each node.

        ``visited`` prevents infinite recursion if cycles exist in the hierarchy.
        """

        nodes = self.world_data.get("nodes", {})
        if parent_lookup is None:
            parent_lookup = {}
            for cid_str, cdata in nodes.items():
                try:
                    cid = int(cid_str)
                except ValueError:
                    continue
                pid = cdata.get("parent_id")
                if isinstance(pid, str) and pid.isdigit():
                    pid = int(pid)
                if isinstance(pid, int):
                    parent_lookup.setdefault(pid, []).append(cid)

        if visited is None:
            visited = set()
        if node_id in visited:
            return {
                "population": 0,
                "soldiers": {},
                "characters": {},
                "animals": {},
                "buildings": {},
            }
        visited.add(node_id)

        def add_count(target: Dict[str, int], key: str, amount: int = 1) -> None:
            if not key:
                return
            target[key] = target.get(key, 0) + amount

        node = nodes.get(str(node_id))
        if not node:
            return {
                "population": 0,
                "soldiers": {},
                "characters": {},
                "animals": {},
                "buildings": {},
            }

        totals = {
            "population": 0,
            "soldiers": {},
            "characters": {},
            "animals": {},
            "buildings": {},
        }

        # Node's own population (ignoring aggregated child totals)
        try:
            pop = (
                int(node.get("free_peasants", 0) or 0)
                + int(node.get("unfree_peasants", 0) or 0)
                + int(node.get("thralls", 0) or 0)
                + int(node.get("burghers", 0) or 0)
            )
        except (ValueError, TypeError):
            pop = 0
        if not pop:
            base = node.get("_base_population")
            try:
                pop = (
                    int(base)
                    if base is not None
                    else int(node.get("population", 0) or 0)
                )
            except (ValueError, TypeError):
                pop = 0
        totals["population"] += pop

        for entry in node.get("soldiers", []):
            t = entry.get("type")
            try:
                c = int(entry.get("count", 0))
            except (ValueError, TypeError):
                c = 0
            add_count(totals["soldiers"], t, c)
        for entry in node.get("characters", []):
            t = entry.get("type")
            add_count(totals["characters"], t, 1)
        for entry in node.get("animals", []):
            t = entry.get("type")
            try:
                c = int(entry.get("count", 0))
            except (ValueError, TypeError):
                c = 0
            add_count(totals["animals"], t, c)
        for entry in node.get("buildings", []):
            t = entry.get("type")
            try:
                c = int(entry.get("count", 0))
            except (ValueError, TypeError):
                c = 0
            add_count(totals["buildings"], t, c)

        child_ids = set(node.get("children", []))
        child_ids.update(parent_lookup.get(node_id, []))
        for child_id in child_ids:
            child_totals = self.calculate_total_resources(
                child_id, visited, parent_lookup
            )
            totals["population"] += child_totals.get("population", 0)
            for key in ("soldiers", "characters", "animals", "buildings"):
                child_dict = child_totals.get(key, {})
                for res, amt in child_dict.items():
                    add_count(totals[key], res, amt)

        node["total_resources"] = copy.deepcopy(totals)
        return totals

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

    def get_children(self, node_id: int) -> List[Node]:
        """Return ``Node`` instances for the direct children of ``node_id``."""

        nodes_dict = self.world_data.get("nodes", {})
        node_data = nodes_dict.get(str(node_id))
        if not node_data:
            return []

        result: List[Node] = []
        for child_id in node_data.get("children", []):
            try:
                cid = int(child_id)
            except (TypeError, ValueError):
                continue
            child_data = nodes_dict.get(str(cid))
            if not child_data:
                continue
            result.append(Node.from_dict(child_data))
        return result

    def get_display_name_for_node(
        self, node_data: Dict[str, Any] | Any, depth: int
    ) -> str:
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
        parent_name: str | None = None
        parent_id = None
        if isinstance(node_data, Node):
            parent_id = node_data.parent_id
        else:
            parent_id = node_data.get("parent_id")
        if parent_id is not None:
            parent = self.world_data.get("nodes", {}).get(str(parent_id))
            if parent:
                parent_custom = str(parent.get("custom_name", "")).strip()
                parent_name = parent_custom or parent.get("name") or f"Nod {parent_id}"
        if depth == 0:
            level_name = name or "Kungarike"
        elif depth == 1:
            level_name = name or "Furstendöme"
        elif depth == 2:
            level_name = name or "Hertigdöme"
        elif depth == 3:
            owner_suffix = f" ({parent_name})" if parent_name else ""
            return f"{custom_name or f'Jarldöme {node_id}'}{owner_suffix}"
        else:
            ruler_str = ""
            if ruler_id and "characters" in self.world_data:
                ruler_data = self.world_data["characters"].get(str(ruler_id))
                if ruler_data:
                    ruler_str = ruler_data.get("name", f"Karaktär {ruler_id}")
            parts: List[str] = []
            if res_type and res_type != "Resurs":
                parts.append(res_type)
            if custom_name and res_type != "Väder":
                parts.append(custom_name)
            if ruler_str:
                parts.append(f"({ruler_str})")
            if not parts:
                owner_suffix = f" ({parent_name})" if parent_name else ""
                return f"Resurs {node_id}{owner_suffix}"
            owner_suffix = f" ({parent_name})" if parent_name else ""
            return " - ".join(parts) + owner_suffix

        display = level_name
        if custom_name and custom_name != level_name:
            display += f" [{custom_name}]"
        if show_id:
            display += f" (ID: {node_id})"
        if parent_name:
            display += f" ({parent_name})"
        return display

    def update_subfiefs_for_node(self, node_data: Dict[str, Any]) -> None:
        current_children_ids = set(node_data.get("children", []))
        if node_data.get("res_type") == "Väder":
            node_data["children"] = []
            node_data["num_subfiefs"] = 0
            return
        target_count = node_data.get("num_subfiefs", 0)
        depth = self.get_depth_of_node(node_data["node_id"])

        next_id = max(
            self.world_data.get("next_node_id", 1),
            max((int(nid) for nid in self.world_data.get("nodes", {})), default=0) + 1,
        )

        while len(current_children_ids) < target_count:
            new_id = next_id
            next_id += 1
            new_id_str = str(new_id)

            if depth == 0:
                child_name = "Furstendöme"
            elif depth == 1:
                child_name = "Hertigdöme"
            elif depth == 2:
                child_name = "Jarldöme"
            else:
                child_name = "Resurs"

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

        self.world_data["next_node_id"] = next_id

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

    def count_descendants(self, node_id: int) -> int:
        """Return the total number of descendant nodes for ``node_id``."""
        nodes = self.world_data.get("nodes", {})
        visited: set[int] = set()

        def recurse(nid: int) -> int:
            if nid in visited:
                return 0
            visited.add(nid)
            node = nodes.get(str(nid))
            if not node:
                return 0
            total = 0
            for child in node.get("children", []):
                total += 1
                total += recurse(child)
            return total

        return recurse(node_id)

    def attempt_link_neighbors(
        self,
        node_id1: int,
        node_id2: int,
        slot1: int | None = None,
        slot2: int | None = None,
    ) -> tuple[bool, str]:
        node1 = self.world_data["nodes"].get(str(node_id1))
        node2 = self.world_data["nodes"].get(str(node_id2))
        if not node1 or not node2:
            return False, "Fel: En eller båda noder kunde inte hittas."
        if (
            self.get_depth_of_node(node_id1) != 3
            or self.get_depth_of_node(node_id2) != 3
        ):
            return False, "Fel: Kan bara länka Jarldömen (nivå 3)."
        neighbors1 = node1.get("neighbors", [])
        neighbors2 = node2.get("neighbors", [])
        if len(neighbors1) < MAX_NEIGHBORS:
            neighbors1.extend(
                {"id": None, "border": NEIGHBOR_NONE_STR}
                for _ in range(MAX_NEIGHBORS - len(neighbors1))
            )
            node1["neighbors"] = neighbors1
        if len(neighbors2) < MAX_NEIGHBORS:
            neighbors2.extend(
                {"id": None, "border": NEIGHBOR_NONE_STR}
                for _ in range(MAX_NEIGHBORS - len(neighbors2))
            )
            node2["neighbors"] = neighbors2
        if any(nb.get("id") == node_id2 for nb in neighbors1) or any(
            nb.get("id") == node_id1 for nb in neighbors2
        ):
            msg = f"Fel: {node1.get('custom_name', f'ID:{node_id1}')} och {node2.get('custom_name', f'ID:{node_id2}')} är redan grannar."
            return False, msg

        def find_free_slot(neighbors: list) -> int | None:
            for i, nb in enumerate(neighbors):
                if nb.get("id") is None:
                    return i
            return None

        if slot1 is not None:
            if not (1 <= slot1 <= MAX_NEIGHBORS):
                return False, "Fel: Ogiltig plats för grannar."
            idx1 = slot1 - 1
            if neighbors1[idx1].get("id") is not None:
                return False, "Fel: Angiven plats är upptagen."
        else:
            fs1 = find_free_slot(neighbors1)
            if fs1 is None:
                return False, "Fel: Inga lediga platser för första jarldömet."
            idx1 = fs1

        if slot2 is None and slot1 is not None:
            slot2 = ((slot1 + 2) % MAX_NEIGHBORS) + 1

        if slot2 is not None:
            if not (1 <= slot2 <= MAX_NEIGHBORS):
                return False, "Fel: Ogiltig plats för grannar."
            idx2 = slot2 - 1
            if neighbors2[idx2].get("id") is not None:
                return False, "Fel: Angiven plats är upptagen."
        else:
            fs2 = find_free_slot(neighbors2)
            if fs2 is None:
                return False, "Fel: Inga lediga platser för andra jarldömet."
            idx2 = fs2

        neighbors1[idx1]["id"] = node_id2
        neighbors1[idx1]["border"] = NEIGHBOR_NONE_STR
        neighbors2[idx2]["id"] = node_id1
        neighbors2[idx2]["border"] = NEIGHBOR_NONE_STR
        node1["neighbors"] = neighbors1
        node2["neighbors"] = neighbors2
        msg = f"{node1.get('custom_name', f'ID:{node_id1}')} och {node2.get('custom_name', f'ID:{node_id2}')} är nu grannar."
        return True, msg

    # -------------------------------------------
    # Bidirectional neighbor management
    # -------------------------------------------
    def update_neighbors_for_node(
        self, node_id: int, new_neighbors: List[Dict[str, Any]]
    ) -> None:
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

        # Add/update reverse links for each new neighbor using directional slots
        for idx, entry in enumerate(new_neighbors):
            nid = entry.get("id")
            if not isinstance(nid, int):
                continue
            other = nodes_dict.get(str(nid))
            if not other:
                continue
            border_val = entry.get("border", NEIGHBOR_NONE_STR)
            other_neighbors = other.get("neighbors", [])
            if len(other_neighbors) < MAX_NEIGHBORS:
                other_neighbors.extend(
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - len(other_neighbors))
                )
                other["neighbors"] = other_neighbors
            opp_idx = (idx + 3) % MAX_NEIGHBORS
            for nb in other_neighbors:
                if nb.get("id") == node_id:
                    nb["id"] = None
                    nb["border"] = NEIGHBOR_NONE_STR
            other_neighbors[opp_idx]["id"] = node_id
            other_neighbors[opp_idx]["border"] = border_val

        node["neighbors"] = new_neighbors

    def set_border_between(
        self, node_id1: int, node_id2: int, border_type: str
    ) -> bool:
        """Set border type for the connection between two nodes."""
        if border_type not in BORDER_TYPES:
            border_type = NEIGHBOR_NONE_STR
        nodes = self.world_data.get("nodes", {})
        n1 = nodes.get(str(node_id1))
        n2 = nodes.get(str(node_id2))
        if not n1 or not n2:
            return False

        changed = False
        for nb in n1.get("neighbors", []):
            if nb.get("id") == node_id2:
                if nb.get("border") != border_type:
                    nb["border"] = border_type
                    changed = True
        for nb in n2.get("neighbors", []):
            if nb.get("id") == node_id1:
                if nb.get("border") != border_type:
                    nb["border"] = border_type
                    changed = True

        return changed
