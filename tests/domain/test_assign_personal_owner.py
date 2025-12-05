import pytest

from src.world_manager import WorldManager


def _world():
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3]},
            "3": {"node_id": 3, "parent_id": 2, "children": [4]},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "children": [],
                "owner_assigned_level": "none",
                "personal_province_path": [],
            },
        }
    }


def test_assign_personal_owner_updates_path_and_owner():
    manager = WorldManager(_world())

    result = manager.assign_personal_owner(4, ("1", 2))

    node = manager.world_data["nodes"]["4"]
    assert result.success
    assert node["owner_assigned_level"] == "1"
    assert node["owner_assigned_id"] == 2
    assert node["personal_province_path"] == [1, 2]


def test_assign_personal_owner_prevents_cycles():
    manager = WorldManager(_world())

    result = manager.assign_personal_owner(2, ("2", 3))

    node = manager.world_data["nodes"]["2"]
    assert not result.success
    assert node.get("owner_assigned_level", "none") == "none"
    assert node.get("owner_assigned_id") is None


def test_assign_personal_owner_creates_snapshot_and_marks_cache():
    manager = WorldManager(_world())

    result = manager.assign_personal_owner(4, ("0", 1))

    assert result.success
    assert manager._snapshots
    assert manager._tax_cache_stale is True
