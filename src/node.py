from dataclasses import dataclass, field
from typing import List, Optional

from constants import MAX_NEIGHBORS, NEIGHBOR_NONE_STR


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
    free_peasants: int = 0
    unfree_peasants: int = 0
    thralls: int = 0
    burghers: int = 0
    craftsmen: List[dict] = field(default_factory=list)
    edited: bool = False

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
        free_peasants = int(data.get("free_peasants", 0) or 0)
        unfree_peasants = int(data.get("unfree_peasants", 0) or 0)
        thralls = int(data.get("thralls", 0) or 0)
        burghers = int(data.get("burghers", 0) or 0)
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

        return cls(
            node_id=node_id,
            parent_id=parent_id,
            name=data.get("name", ""),
            custom_name=data.get("custom_name", ""),
            population=int(data.get("population", 0)),
            ruler_id=ruler_id,
            num_subfiefs=int(data.get("num_subfiefs", 0)),
            children=children,
            neighbors=neighbors,
            res_type=data.get("res_type", "Resurs"),
            settlement_type=settlement_type,
            free_peasants=free_peasants,
            unfree_peasants=unfree_peasants,
            thralls=thralls,
            burghers=burghers,
            craftsmen=craftsmen,
            edited=bool(data.get("edited", False)),
        )

    def to_dict(self) -> dict:
        """Convert this Node back into a serialisable dictionary."""
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "custom_name": self.custom_name,
            "population": self.population,
            "ruler_id": self.ruler_id,
            "num_subfiefs": self.num_subfiefs,
            "children": list(self.children),
            "neighbors": [
                {"id": nb.id, "border": nb.border} for nb in self.neighbors
            ],
            "res_type": self.res_type,
            "settlement_type": self.settlement_type,
            "free_peasants": self.free_peasants,
            "unfree_peasants": self.unfree_peasants,
            "thralls": self.thralls,
            "burghers": self.burghers,
            "craftsmen": [
                {"type": c.get("type", ""), "count": c.get("count", 1)}
                for c in self.craftsmen
            ],
            "edited": self.edited,
        }
