import pytest

from src.world_manager import WorldManager


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
