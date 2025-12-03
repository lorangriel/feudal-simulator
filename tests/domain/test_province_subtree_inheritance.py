import pytest

from feodal_simulator import FeodalSimulator
from world_manager import WorldManager


OWNER_X = 101
OWNER_Y = 202


def _make_simulator(assignments: dict[int, tuple[str, int]] | None = None) -> FeodalSimulator:
    assignments = assignments or {}
    nodes = {}
    for node_id in range(1, 5):
        parent_id = node_id - 1 if node_id > 1 else None
        owner_level, owner_id = assignments.get(node_id, ("none", None))
        nodes[str(node_id)] = {
            "node_id": node_id,
            "name": f"Node {node_id}",
            "parent_id": parent_id,
            "children": [node_id + 1] if node_id < 4 else [],
            "owner_assigned_level": owner_level,
            "owner_assigned_id": owner_id,
        }

    world_data = {"nodes": nodes}

    sim = FeodalSimulator.__new__(FeodalSimulator)
    sim.world_data = world_data
    sim.world_manager = WorldManager(world_data)

    return sim


def test_province_subtree_inherits_downward():
    sim = _make_simulator({2: ("1", OWNER_X)})

    subtree = sim.get_province_subtree(OWNER_X)

    assert subtree == [
        {"id": 2, "children": [{"id": 3, "children": [{"id": 4, "children": []}]}]}
    ]


def test_province_subtree_breaks_when_child_gets_owner():
    sim = _make_simulator({2: ("1", OWNER_X), 3: ("1", OWNER_Y)})

    subtree_x = sim.get_province_subtree(OWNER_X)
    subtree_y = sim.get_province_subtree(OWNER_Y)

    assert subtree_x == [{"id": 2, "children": []}]
    assert subtree_y == [{"id": 3, "children": [{"id": 4, "children": []}]}]
