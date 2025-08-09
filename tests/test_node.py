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
    assert node.dagsverken == "normalt"
    assert node.work_available == 0
    assert node.work_needed == 0
    assert node.storage_silver == 0
    assert node.storage_basic == 0
    assert node.storage_luxury == 0
    assert node.lager_text == ""
    assert node.storage_timber == 0
    assert node.storage_coal == 0
    assert node.storage_iron_ore == 0
    assert node.storage_iron == 0
    assert node.storage_animal_feed == 0
    assert node.storage_skin == 0
    assert node.jarldom_area == 0
    assert node.expected_license_income == 0
    assert node.umbarande == 0


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


def test_node_dagsverken_roundtrip():
    raw = {
        "node_id": 60,
        "parent_id": 1,
        "dagsverken": "många",
    }

    node = Node.from_dict(raw)
    assert node.dagsverken == "många"

    back = node.to_dict()
    assert back["dagsverken"] == "många"


def test_node_jarldom_extra_fields_roundtrip():
    raw = {
        "node_id": 61,
        "parent_id": 1,
        "work_available": 5,
        "work_needed": 7,
        "umbarande": 4,
        "storage_silver": 10,
        "storage_basic": 3,
        "storage_luxury": 1,
        "jarldom_area": 50,
        "expected_license_income": 12,
    }

    node = Node.from_dict(raw)
    assert node.work_available == 5
    assert node.work_needed == 7
    assert node.umbarande == 4
    assert node.storage_silver == 10
    assert node.storage_basic == 3
    assert node.storage_luxury == 1
    assert node.jarldom_area == 50
    assert node.expected_license_income == 12

    back = node.to_dict()
    assert back["work_available"] == 5
    assert back["work_needed"] == 7
    assert back["umbarande"] == 4
    assert back["storage_silver"] == 10
    assert back["storage_basic"] == 3
    assert back["storage_luxury"] == 1
    assert back["jarldom_area"] == 50
    assert back["expected_license_income"] == 12


def test_node_lager_roundtrip():
    raw = {
        "node_id": 200,
        "parent_id": 1,
        "res_type": "Lager",
        "lager_text": "notes",
        "storage_basic": 1,
        "storage_luxury": 2,
        "storage_silver": 3,
        "storage_timber": 4,
        "storage_coal": 5,
        "storage_iron_ore": 6,
        "storage_iron": 7,
        "storage_animal_feed": 8,
        "storage_skin": 9,
    }
    node = Node.from_dict(raw)
    assert node.lager_text == "notes"
    assert node.storage_timber == 4
    assert node.storage_coal == 5
    assert node.storage_iron_ore == 6
    assert node.storage_iron == 7
    assert node.storage_animal_feed == 8
    assert node.storage_skin == 9
    back = node.to_dict()
    assert back["lager_text"] == "notes"
    assert back["storage_timber"] == 4
    assert back["storage_coal"] == 5
    assert back["storage_iron_ore"] == 6
    assert back["storage_iron"] == 7
    assert back["storage_animal_feed"] == 8
    assert back["storage_skin"] == 9


def test_node_day_laborers_roundtrip():
    raw = {
        "node_id": 70,
        "parent_id": 1,
        "day_laborers_available": 5,
        "day_laborers_hired": 3,
    }

    node = Node.from_dict(raw)
    assert node.day_laborers_available == 5
    assert node.day_laborers_hired == 3

    back = node.to_dict()
    assert back["day_laborers_available"] == 5
    assert back["day_laborers_hired"] == 3


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


def test_node_ignores_animals_for_non_djur():
    raw = {
        "node_id": 32,
        "parent_id": 1,
        "res_type": "Resurs",
        "animals": [{"type": "Oxe", "count": 2}],
    }

    node = Node.from_dict(raw)
    assert node.animals == []

    back = node.to_dict()
    assert "animals" not in back


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


def test_node_jaktmark_roundtrip():
    raw = {
        "node_id": 45,
        "parent_id": 1,
        "res_type": "Jaktmark",
        "tunnland": 12,
        "hunters": 3,
        "gamekeeper_id": "5",
    }

    node = Node.from_dict(raw)
    assert node.tunnland == 12
    assert node.hunters == 3
    assert node.gamekeeper_id == 5
    assert node.population == 0

    back = node.to_dict()
    assert back["tunnland"] == 12
    assert back["hunters"] == 3
    assert back["gamekeeper_id"] == 5


def test_node_mark_land_roundtrip():
    raw = {
        "node_id": 41,
        "parent_id": 1,
        "res_type": "Mark",
        "total_land": 20,
        "forest_land": 15,
        "cleared_land": 5,
    }

    node = Node.from_dict(raw)

    assert node.total_land == 20
    assert node.forest_land == 15
    assert node.cleared_land == 5

    back = node.to_dict()
    assert back["total_land"] == 20
    assert back["forest_land"] == 15
    assert back["cleared_land"] == 5


def test_node_gods_roundtrip():
    raw = {
        "node_id": 80,
        "parent_id": 1,
        "res_type": "Gods",
        "manor_land": 100,
        "cultivated_land": 60,
        "cultivated_quality": 4,
        "fallow_land": 20,
        "has_herd": True,
        "forest_land": 20,
        "hunt_quality": 5,
        "hunting_law": 2,
    }

    node = Node.from_dict(raw)
    assert node.manor_land == 100
    assert node.cultivated_land == 60
    assert node.cultivated_quality == 4
    assert node.fallow_land == 20
    assert node.has_herd is True
    assert node.forest_land == 20
    assert node.hunt_quality == 5
    assert node.hunting_law == 2

    back = node.to_dict()
    assert back["manor_land"] == 100
    assert back["cultivated_land"] == 60
    assert back["cultivated_quality"] == 4
    assert back["fallow_land"] == 20
    assert back["has_herd"] is True
    assert back["forest_land"] == 20
    assert back["hunt_quality"] == 5
    assert back["hunting_law"] == 2


def test_node_water_fields_roundtrip():
    raw = {
        "node_id": 70,
        "parent_id": 1,
        "res_type": "Hav",
        "fish_quality": "ganska bra",
        "fishing_boats": 5,
    }

    node = Node.from_dict(raw)
    assert node.fish_quality == "ganska bra"
    assert node.fishing_boats == 5

    back = node.to_dict()
    assert back["fish_quality"] == "ganska bra"
    assert back["fishing_boats"] == 5


def test_node_water_fields_ignored_for_other_types():
    raw = {
        "node_id": 71,
        "parent_id": 1,
        "res_type": "Vildmark",
        "fish_quality": "bäst",
        "fishing_boats": 10,
    }

    node = Node.from_dict(raw)
    assert node.fish_quality == "Normalt"
    assert node.fishing_boats == 0

    back = node.to_dict()
    assert "fish_quality" not in back
    assert "fishing_boats" not in back


def test_node_river_level_roundtrip():
    raw = {
        "node_id": 72,
        "parent_id": 1,
        "res_type": "Flod",
        "river_level": 3,
    }

    node = Node.from_dict(raw)
    assert node.river_level == 3

    back = node.to_dict()
    assert back["river_level"] == 3


def test_node_river_level_ignored_for_other_types():
    raw = {
        "node_id": 73,
        "parent_id": 1,
        "res_type": "Hav",
        "river_level": 5,
    }

    node = Node.from_dict(raw)
    assert node.river_level == 1

    back = node.to_dict()
    assert "river_level" not in back


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


def test_node_res_type_invalid_defaults_to_resurs():
    raw = {"node_id": 60, "parent_id": None, "res_type": 123}

    node = Node.from_dict(raw)

    assert node.res_type == "Resurs"

    back = node.to_dict()
    assert back["res_type"] == "Resurs"


def test_weather_node_clears_custom_name():
    raw = {
        "node_id": 99,
        "parent_id": 1,
        "res_type": "Väder",
        "custom_name": "Storm",
        "spring_weather": "Varmt och stabilt (-1)",
    }

    node = Node.from_dict(raw)
    assert node.custom_name == ""

    back = node.to_dict()
    assert "custom_name" not in back
    assert back["spring_weather"] == "Varmt och stabilt (-1)"
