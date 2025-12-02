from node import Node


def test_personal_fields_roundtrip_defaults():
    data = {"node_id": 1, "parent_id": None, "children": []}
    node = Node.from_dict(data)
    exported = node.to_dict()
    assert exported["owner_assigned_level"] == "none"
    assert exported["owner_assigned_id"] is None
    assert exported["personal_province_path"] == []
    assert exported["tax_forward_fraction"] + exported["keep_fraction"] == 1


def test_personal_fields_parsing_and_normalisation():
    data = {
        "node_id": 2,
        "parent_id": None,
        "children": [],
        "owner_assigned_level": "1",
        "owner_assigned_id": "9",
        "personal_province_path": [0, "9", 2],
        "keep_fraction": 0.7,
        "tax_forward_fraction": 0.4,
    }
    node = Node.from_dict(data)
    assert node.owner_assigned_level == "1"
    assert node.owner_assigned_id == 9
    assert node.personal_province_path == [0, 9, 2]
    assert abs(node.keep_fraction + node.tax_forward_fraction - 1.0) < 1e-6
