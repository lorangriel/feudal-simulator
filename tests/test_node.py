from src.node import Node
from src.constants import NEIGHBOR_NONE_STR, MAX_NEIGHBORS


def test_node_from_dict_normalizes_fields():
    raw = {
        "node_id": 1,
        "parent_id": None,
        "name": "Kingdom",
        "custom_name": "Svea",
        "population": 100,
        "ruler_id": "2",
        "num_subfiefs": 0,
        "children": ["2", 3],
        "neighbors": [{"id": "2", "border": "v\u00e4g"}],
        "res_type": "Resurs",
    }

    node = Node.from_dict(raw)

    assert node.node_id == 1
    assert node.parent_id is None
    assert node.ruler_id == 2
    assert node.children == [2, 3]
    assert len(node.neighbors) == MAX_NEIGHBORS
    assert node.neighbors[0].id == 2
    assert node.neighbors[0].border == "v\u00e4g"
    for nb in node.neighbors[1:]:
        assert nb.id is None and nb.border == NEIGHBOR_NONE_STR
    # New settlement fields should have defaults
    assert node.settlement_type == "By"
    assert node.free_peasants == 0
    assert node.unfree_peasants == 0
    assert node.thralls == 0
    assert node.burghers == 0
    assert node.craftsmen == []


def test_node_settlement_roundtrip():
    raw = {
        "node_id": 5,
        "parent_id": 1,
        "settlement_type": "Stad",
        "free_peasants": "10",
        "unfree_peasants": 5,
        "thralls": "2",
        "burghers": 7,
        "craftsmen": [
            {"type": "Smed", "count": "3"},
            {"type": "Bagare", "count": 1},
        ],
    }

    node = Node.from_dict(raw)
    assert node.settlement_type == "Stad"
    assert node.free_peasants == 10
    assert node.unfree_peasants == 5
    assert node.thralls == 2
    assert node.burghers == 7
    assert node.craftsmen == [
        {"type": "Smed", "count": 3},
        {"type": "Bagare", "count": 1},
    ]

    back = node.to_dict()
    assert back["settlement_type"] == "Stad"
    assert back["free_peasants"] == 10
    assert back["unfree_peasants"] == 5
    assert back["thralls"] == 2
    assert back["burghers"] == 7
    assert back["craftsmen"] == [
        {"type": "Smed", "count": 3},
        {"type": "Bagare", "count": 1},
    ]


def test_node_population_calculated_from_categories():
    raw = {
        "node_id": 8,
        "parent_id": 1,
        "free_peasants": 3,
        "unfree_peasants": 2,
        "thralls": 1,
        "burghers": 4,
    }
    node = Node.from_dict(raw)
    assert node.population == 10
    data = node.to_dict()
    assert data["population"] == 10
