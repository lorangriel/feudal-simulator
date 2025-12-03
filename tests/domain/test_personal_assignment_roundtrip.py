import pytest

from node import Node
from personal_province import build_personal_path


@pytest.mark.parametrize(
    "owner_level,expected_path",
    [("0", [100]), ("1", [100, 200]), ("2", [100, 200, 300])],
)
def test_personal_assignment_roundtrip(owner_level, expected_path):
    owner_id = 42
    jarldom_data = {
        "node_id": 400,
        "parent_id": 300,
        "children": [],
        "owner_assigned_level": owner_level,
        "owner_assigned_id": owner_id,
        "personal_province_path": build_personal_path(
            owner_level, owner_id, [100, 200, 300]
        ),
    }

    jarldom = Node.from_dict(jarldom_data)
    exported = jarldom.to_dict()

    assert exported["owner_assigned_level"] == owner_level
    assert exported["owner_assigned_id"] == owner_id
    assert exported["personal_province_path"] == expected_path

    restored = Node.from_dict(exported).to_dict()
    assert restored["owner_assigned_level"] == owner_level
    assert restored["owner_assigned_id"] == owner_id
    assert restored["personal_province_path"] == expected_path


def test_personal_assignment_roundtrip_local_default():
    jarldom_data = {
        "node_id": 401,
        "parent_id": 300,
        "children": [],
        "owner_assigned_level": "none",
        "owner_assigned_id": None,
        "personal_province_path": [],
    }

    jarldom = Node.from_dict(jarldom_data)
    exported = jarldom.to_dict()

    assert exported["owner_assigned_level"] == "none"
    assert exported["owner_assigned_id"] is None
    assert exported["personal_province_path"] == []

    restored = Node.from_dict(exported).to_dict()
    assert restored["owner_assigned_level"] == "none"
    assert restored["owner_assigned_id"] is None
    assert restored["personal_province_path"] == []
