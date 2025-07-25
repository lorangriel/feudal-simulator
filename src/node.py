from dataclasses import dataclass, field
from typing import List, Optional

from constants import (
    MAX_NEIGHBORS,
    NEIGHBOR_NONE_STR,
    DAGSVERKEN_LEVELS,
    FISH_QUALITY_LEVELS,
    MAX_FISHING_BOATS,
)


@dataclass
class Neighbor:
    """Represents one neighbor connection for a node."""
    id: Optional[int] = None
    border: str = NEIGHBOR_NONE_STR


@dataclass
class Node:
    """Simple object representation of a node in a world."""

    node_id: int
    parent_id: Optional[int]
    name: str = ""
    custom_name: str = ""
    population: int = 0
    ruler_id: Optional[int] = None
    num_subfiefs: int = 0
    children: List[int] = field(default_factory=list)
    neighbors: List[Neighbor] = field(default_factory=list)
    res_type: str = "Resurs"
    settlement_type: str = "By"
    dagsverken: str = "normalt"
    free_peasants: int = 0
    unfree_peasants: int = 0
    thralls: int = 0
    burghers: int = 0
    tunnland: int = 0  # Area for wilderness resources measured in tunnland
    craftsmen: List[dict] = field(default_factory=list)
    soldiers: List[dict] = field(default_factory=list)
    characters: List[dict] = field(default_factory=list)
    animals: List[dict] = field(default_factory=list)
    buildings: List[dict] = field(default_factory=list)
    fish_quality: str = "Normalt"
    fishing_boats: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """Create a Node from a dictionary of raw world data."""
        node_id = int(data.get("node_id"))
        parent_id = data.get("parent_id")
        if isinstance(parent_id, str) and parent_id.isdigit():
            parent_id = int(parent_id)
        elif parent_id is not None and not isinstance(parent_id, int):
            parent_id = None

        ruler_id = data.get("ruler_id")
        if isinstance(ruler_id, str) and ruler_id.isdigit():
            ruler_id = int(ruler_id)
        elif ruler_id is not None and not isinstance(ruler_id, int):
            ruler_id = None

        children = [int(c) for c in data.get("children", []) if str(c).isdigit()]

        # Normalise neighbor list to MAX_NEIGHBORS entries
        neighbors_raw = data.get("neighbors", [])
        neighbors: List[Neighbor] = []
        for i in range(MAX_NEIGHBORS):
            if i < len(neighbors_raw) and isinstance(neighbors_raw[i], dict):
                ndata = neighbors_raw[i]
                nid = ndata.get("id")
                if isinstance(nid, str) and nid.isdigit():
                    nid = int(nid)
                border = ndata.get("border", NEIGHBOR_NONE_STR)
                neighbors.append(Neighbor(nid, border))
            else:
                neighbors.append(Neighbor())

        settlement_type = data.get("settlement_type", "By")
        dagsverken = data.get("dagsverken", "normalt")
        if dagsverken not in DAGSVERKEN_LEVELS:
            dagsverken = "normalt"
        free_peasants = int(data.get("free_peasants", 0) or 0)
        unfree_peasants = int(data.get("unfree_peasants", 0) or 0)
        thralls = int(data.get("thralls", 0) or 0)
        burghers = int(data.get("burghers", 0) or 0)
        tunnland = int(data.get("tunnland", 0) or 0)
        base_pop = int(data.get("population", 0) or 0)
        computed_pop = free_peasants + unfree_peasants + thralls + burghers
        res_type_raw = data.get("res_type", "Resurs")
        res_type = res_type_raw if isinstance(res_type_raw, str) and res_type_raw else "Resurs"
        if res_type == "Vildmark":
            population = 0
        elif computed_pop:
            population = computed_pop
        else:
            population = base_pop
        craftsmen_raw = data.get("craftsmen", [])
        craftsmen: List[dict] = []
        if isinstance(craftsmen_raw, list):
            for c in craftsmen_raw:
                if not isinstance(c, dict):
                    continue
                ctype = c.get("type", "")
                count = c.get("count", 1)
                try:
                    count_int = int(count)
                except (ValueError, TypeError):
                    count_int = 1
                craftsmen.append({"type": str(ctype), "count": max(1, min(count_int, 9))})

        def parse_list_of_dict(key: str, count_field: bool = False) -> List[dict]:
            items_raw = data.get(key, [])
            items: List[dict] = []
            if isinstance(items_raw, list):
                for entry in items_raw:
                    if not isinstance(entry, dict):
                        continue
                    tval = entry.get("type", "")
                    if count_field:
                        count = entry.get("count", 1)
                        try:
                            cnt = int(count)
                        except (ValueError, TypeError):
                            cnt = 1
                        items.append({"type": str(tval), "count": max(0, cnt)})
                    else:
                        rid = entry.get("ruler_id")
                        if isinstance(rid, str) and rid.isdigit():
                            rid = int(rid)
                        elif rid is not None and not isinstance(rid, int):
                            rid = None
                        items.append({"type": str(tval), "ruler_id": rid})
            return items

        soldiers: List[dict] = []
        animals: List[dict] = []
        if data.get("res_type") == "Soldater" or "soldiers" in data:
            soldiers = parse_list_of_dict("soldiers", count_field=True)
        if data.get("res_type") == "Djur":
            animals = parse_list_of_dict("animals", count_field=True)
        characters = parse_list_of_dict("characters", count_field=False)
        buildings = parse_list_of_dict("buildings", count_field=True)

        fish_quality = "Normalt"
        fishing_boats = 0
        if res_type in {"Hav", "Flod"}:
            wq_raw = data.get("fish_quality", data.get("water_quality", "Normalt"))
            fish_quality = (
                wq_raw if isinstance(wq_raw, str) and wq_raw in FISH_QUALITY_LEVELS else "Normalt"
            )
            try:
                fishing_boats = int(data.get("fishing_boats", 0) or 0)
            except (ValueError, TypeError):
                fishing_boats = 0
            fishing_boats = max(0, min(fishing_boats, MAX_FISHING_BOATS))

        return cls(
            node_id=node_id,
            parent_id=parent_id,
            name=data.get("name", ""),
            custom_name=data.get("custom_name", ""),
            population=population,
            ruler_id=ruler_id,
            num_subfiefs=int(data.get("num_subfiefs", 0)),
            children=children,
            neighbors=neighbors,
            res_type=res_type,
            settlement_type=settlement_type,
            dagsverken=dagsverken,
            free_peasants=free_peasants,
            unfree_peasants=unfree_peasants,
            thralls=thralls,
            burghers=burghers,
            tunnland=tunnland,
            craftsmen=craftsmen,
            soldiers=soldiers,
            characters=characters,
            animals=animals,
            buildings=buildings,
            fish_quality=fish_quality,
            fishing_boats=fishing_boats,
        )

    def to_dict(self) -> dict:
        """Convert this Node back into a serialisable dictionary."""
        data = {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "custom_name": self.custom_name,
            "population": self.calculate_population(),
            "ruler_id": self.ruler_id,
            "num_subfiefs": self.num_subfiefs,
            "children": list(self.children),
            "neighbors": [
                {"id": nb.id, "border": nb.border} for nb in self.neighbors
            ],
            "res_type": str(self.res_type) if self.res_type is not None else "Resurs",
            "settlement_type": self.settlement_type,
            "dagsverken": self.dagsverken,
            "free_peasants": self.free_peasants,
            "unfree_peasants": self.unfree_peasants,
            "thralls": self.thralls,
            "burghers": self.burghers,
            "tunnland": self.tunnland,
            "craftsmen": [
                {"type": c.get("type", ""), "count": c.get("count", 1)}
                for c in self.craftsmen
            ],
            "characters": [
                {"type": c.get("type", ""), "ruler_id": c.get("ruler_id")}
                for c in self.characters
            ],
            "buildings": [
                {"type": b.get("type", ""), "count": b.get("count", 1)}
                for b in self.buildings
            ],
        }

        if self.res_type == "Soldater":
            data["soldiers"] = [
                {"type": s.get("type", ""), "count": s.get("count", 1)}
                for s in self.soldiers
            ]

        if self.res_type == "Djur":
            data["animals"] = [
                {"type": a.get("type", ""), "count": a.get("count", 1)}
                for a in self.animals
            ]

        if self.res_type in {"Hav", "Flod"}:
            data["fish_quality"] = self.fish_quality
            data["fishing_boats"] = self.fishing_boats

        return data

    def calculate_population(self) -> int:
        """Return the total population for this node based on categories."""
        total = (
            self.free_peasants
            + self.unfree_peasants
            + self.thralls
            + self.burghers
        )
        return total if total else self.population
