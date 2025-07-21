import pytest

from src.world_manager import WorldManager
from src.world_interface import WorldInterface
from src.constants import BORDER_TYPES, MAX_NEIGHBORS, NEIGHBOR_NONE_STR
import json
import os
import tempfile


def test_init_with_world_data():
    data = {"nodes": {}, "characters": {}}
    manager = WorldManager(data)
    assert manager.world_data == data


def test_set_world_data_replaces_reference():
    manager = WorldManager()
    new_data = {"nodes": {"1": {"node_id": 1}}}
    manager.set_world_data(new_data)
    assert manager.world_data is new_data


def test_delete_node_and_descendants_removes_subtree():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2], "num_subfiefs": 1},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "num_subfiefs": 1},
            "3": {"node_id": 3, "parent_id": 2, "children": [], "num_subfiefs": 0},
        },
        "characters": {},
        "next_node_id": 3,
    }
    manager = WorldManager(world)
    deleted = manager.delete_node_and_descendants(2)
    assert deleted == 2
    assert "2" not in world["nodes"]
    assert "3" not in world["nodes"]
    assert world["nodes"]["1"]["children"] == []


def test_delete_node_and_descendants_missing_node():
    manager = WorldManager({"nodes": {}, "characters": {}})
    assert manager.delete_node_and_descendants(99) == 0


def test_world_file_helpers(tmp_path):
    data = {"a": 1}
    file_path = tmp_path / "worlds.json"
    # Test save
    WorldInterface.save_worlds_file(data, file_path)
    assert file_path.exists()
    # Test load
    loaded = WorldInterface.load_worlds_file(file_path)
    assert loaded == data
    # Missing file returns empty dict
    missing = WorldInterface.load_worlds_file(tmp_path / "missing.json")
    assert missing == {}


def test_validate_world_data_basic():
    world = {
        "nodes": {
            "1": {"parent_id": None, "children": [2], "num_subfiefs": 1},
            "2": {
                "parent_id": 1,
                "children": [3],
                "ruler_id": 99,
                "neighbors": [{"id": "X", "border": "bogus"}],
            },
        },
        "characters": {"10": {"name": "Hero"}},
    }
    manager = WorldManager(world)
    # Force depths: root=0, jarldom=3
    manager.get_depth_of_node = lambda nid: 0 if nid == 1 else 3
    nodes_updated, chars_updated = manager.validate_world_data()
    assert nodes_updated > 0
    assert chars_updated > 0
    node1 = world["nodes"]["1"]
    node2 = world["nodes"]["2"]
    assert node1["node_id"] == 1
    assert node2["neighbors"][0]["border"] in BORDER_TYPES
    assert len(node2["neighbors"]) == MAX_NEIGHBORS
    assert node2["children"] == []
    assert node2["ruler_id"] is None
    assert world["characters"]["10"]["char_id"] == 10


def test_validate_world_data_vildmark_defaults():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "res_type": "Vildmark",
            }
        },
        "characters": {},
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda _nid: 4
    nodes_updated, _ = manager.validate_world_data()
    assert nodes_updated > 0
    node = world["nodes"]["1"]
    assert "tunnland" in node
    assert "population" not in node


def test_update_neighbors_for_node_bidirectional():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {
                "node_id": 10,
                "parent_id": 1,
                "neighbors": [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS)
                ],
            },
            "20": {
                "node_id": 20,
                "parent_id": 1,
                "neighbors": [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS)
                ],
            },
        },
        "characters": {},
        "next_node_id": 20,
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: 3 if nid in (10, 20) else 0

    new_neighbors = [
        {"id": 20, "border": "v\u00e4g"}
    ] + [
        {"id": None, "border": NEIGHBOR_NONE_STR}
        for _ in range(MAX_NEIGHBORS - 1)
    ]

    manager.update_neighbors_for_node(10, new_neighbors)

    assert world["nodes"]["10"]["neighbors"][0]["id"] == 20
    back = None
    for nb in world["nodes"]["20"]["neighbors"]:
        if nb.get("id") == 10:
            back = nb
            break
    assert back is not None
    assert back["border"] == "v\u00e4g"

    empty_neighbors = [
        {"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)
    ]
    manager.update_neighbors_for_node(10, empty_neighbors)
    assert all(nb.get("id") != 10 for nb in world["nodes"]["20"]["neighbors"])


def test_update_neighbors_handles_truncated_lists():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {"node_id": 10, "parent_id": 1, "neighbors": []},
            "20": {
                "node_id": 20,
                "parent_id": 1,
                "neighbors": [{"id": None, "border": NEIGHBOR_NONE_STR}],
            },
        },
        "characters": {},
        "next_node_id": 20,
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: 3 if nid in (10, 20) else 0

    new_neighbors = [
        {"id": 20, "border": "v\u00e4g"}
    ] + [
        {"id": None, "border": NEIGHBOR_NONE_STR}
        for _ in range(MAX_NEIGHBORS - 1)
    ]

    manager.update_neighbors_for_node(10, new_neighbors)

    assert len(world["nodes"]["10"]["neighbors"]) == MAX_NEIGHBORS
    assert len(world["nodes"]["20"]["neighbors"]) == MAX_NEIGHBORS
    assert world["nodes"]["10"]["neighbors"][0]["id"] == 20
    assert any(nb.get("id") == 10 for nb in world["nodes"]["20"]["neighbors"])
