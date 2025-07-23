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


def test_node_soldier_roundtrip():
    raw = {
        "node_id": 20,
        "parent_id": 1,
        "res_type": "Soldater",
        "soldiers": [{"type": "B\u00e5gskytt", "count": "2"}],
        "characters": [{"type": "Officer", "ruler_id": "5"}],
        "buildings": [{"type": "Smedja", "count": "1"}],
    }
    node = Node.from_dict(raw)
    assert node.soldiers == [{"type": "B\u00e5gskytt", "count": 2}]
    assert node.characters == [{"type": "Officer", "ruler_id": 5}]
    assert node.animals == []
    assert node.buildings == [{"type": "Smedja", "count": 1}]

    back = node.to_dict()
    assert back["soldiers"] == [{"type": "B\u00e5gskytt", "count": 2}]
    assert back["characters"] == [{"type": "Officer", "ruler_id": 5}]
    assert "animals" not in back
    assert back["buildings"] == [{"type": "Smedja", "count": 1}]


def test_node_animal_roundtrip():
    raw = {
        "node_id": 21,
        "parent_id": 1,
        "res_type": "Djur",
        "animals": [{"type": "Oxe", "count": 3}],
        "characters": [],
        "buildings": [],
    }
    node = Node.from_dict(raw)
    assert node.soldiers == []
    assert node.animals == [{"type": "Oxe", "count": 3}]

    back = node.to_dict()
    assert back["animals"] == [{"type": "Oxe", "count": 3}]
    assert "soldiers" not in back


def test_node_soldier_large_count():
    raw = {
        "node_id": 30,
        "parent_id": 1,
        "res_type": "Soldater",
        "soldiers": [{"type": "Fotsoldat", "count": "123456"}],
    }

    node = Node.from_dict(raw)
    assert node.soldiers == [{"type": "Fotsoldat", "count": 123456}]

    back = node.to_dict()
    assert back["soldiers"] == [{"type": "Fotsoldat", "count": 123456}]


def test_node_animal_large_count():
    raw = {
        "node_id": 31,
        "parent_id": 1,
        "res_type": "Djur",
        "animals": [{"type": "Oxe", "count": "654321"}],
    }

    node = Node.from_dict(raw)
    assert node.animals == [{"type": "Oxe", "count": 654321}]

    back = node.to_dict()
    assert back["animals"] == [{"type": "Oxe", "count": 654321}]


def test_node_vildmark_tunnland_roundtrip():
    raw = {
        "node_id": 40,
        "parent_id": 1,
        "res_type": "Vildmark",
        "tunnland": 7,
    }

    node = Node.from_dict(raw)
    assert node.tunnland == 7
    assert node.population == 0

    back = node.to_dict()
    assert back["tunnland"] == 7
    assert back["population"] == 0


def test_node_characters_roundtrip():
    raw = {
        "node_id": 50,
        "parent_id": 1,
        "characters": [
            {"type": "Officer"},
            {"type": "Härskare", "ruler_id": 3},
        ],
    }

    node = Node.from_dict(raw)
    assert node.characters == [
        {"type": "Officer", "ruler_id": None},
        {"type": "Härskare", "ruler_id": 3},
    ]

    back = node.to_dict()
    assert back["characters"] == [
        {"type": "Officer", "ruler_id": None},
        {"type": "Härskare", "ruler_id": 3},
    ]
