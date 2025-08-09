from src.world_manager import WorldManager
from src.constants import (
    MAX_NEIGHBORS,
    NEIGHBOR_NONE_STR,
    DAGSVERKEN_MULTIPLIERS,
    THRALL_WORK_DAYS,
    DAGSVERKEN_UMBARANDE,
    DAY_LABORER_WORK_DAYS,
)


def test_attempt_link_neighbors_directional():
    world = {
        "nodes": {
            "10": {"node_id": 10, "parent_id": 1, "neighbors": [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]},
        },
        "characters": {},
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda _nid: 3

    ok, _ = manager.attempt_link_neighbors(10, 20, slot1=2)
    assert ok
    assert world["nodes"]["10"]["neighbors"][1]["id"] == 20
    assert world["nodes"]["20"]["neighbors"][4]["id"] == 10


def test_aggregate_resources_simple():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2, 3]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "soldiers": [{"type": "B\u00e5gskytt", "count": 2}],
                "animals": [{"type": "Oxe", "count": 1}],
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "children": [],
                "soldiers": [
                    {"type": "B\u00e5gskytt", "count": 1},
                    {"type": "Fotsoldat", "count": 3},
                ],
            },
        },
        "characters": {},
    }
    manager = WorldManager(world)
    totals = manager.aggregate_resources(1)
    assert totals["soldiers"]["B\u00e5gskytt"] == 3
    assert totals["soldiers"]["Fotsoldat"] == 3
    assert totals["animals"]["Oxe"] == 1


def test_aggregate_resources_buildings():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "buildings": [
                    {"type": "Smedja", "count": 1},
                    {"type": "Bageri", "count": 2},
                ],
            },
        },
        "characters": {},
    }
    manager = WorldManager(world)
    totals = manager.aggregate_resources(1)
    assert totals["buildings"]["Smedja"] == 1
    assert totals["buildings"]["Bageri"] == 2


def test_calculate_total_resources_recursive():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2, 3],
                "free_peasants": 3,
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [4],
                "soldiers": [{"type": "Archer", "count": 2}],
                "population": 5,
            },
            "3": {"node_id": 3, "parent_id": 1, "children": [], "population": 4},
            "4": {
                "node_id": 4,
                "parent_id": 2,
                "children": [],
                "free_peasants": 1,
                "burghers": 1,
                "soldiers": [{"type": "Archer", "count": 1}],
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    totals = manager.calculate_total_resources(1)

    assert totals["population"] == 14
    assert totals["soldiers"]["Archer"] == 3
    assert world["nodes"]["2"]["total_resources"]["population"] == 7
    assert world["nodes"]["4"]["total_resources"]["population"] == 2


def test_calculate_total_resources_cycle():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [1],  # cycle back to root
                "population": 5,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    totals = manager.calculate_total_resources(1)

    assert totals["population"] == 5
    assert world["nodes"]["1"]["total_resources"]["population"] == 5
    assert world["nodes"]["2"]["total_resources"]["population"] == 5


def test_total_resources_uses_base_population():
    """Population totals should not double count aggregated values."""
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [4]},
            "4": {"node_id": 4, "parent_id": 1, "children": [], "res_type": "Gods"},
            "5": {
                "node_id": 5,
                "parent_id": 4,
                "children": [],
                "res_type": "Bosättning",
                "free_peasants": 6,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: {1: 0, 4: 1, 5: 2}[nid]

    manager.update_population_totals()
    totals = manager.calculate_total_resources(1)

    assert totals["population"] == 6
    assert world["nodes"]["1"]["total_resources"]["population"] == 6
    assert world["nodes"]["4"]["total_resources"]["population"] == 6


def test_count_descendants_simple_hierarchy():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2, 3]},
            "2": {"node_id": 2, "parent_id": 1, "children": [4]},
            "3": {"node_id": 3, "parent_id": 1, "children": []},
            "4": {"node_id": 4, "parent_id": 2, "children": []},
        },
        "characters": {},
    }

    manager = WorldManager(world)

    assert manager.count_descendants(1) == 3
    assert manager.count_descendants(2) == 1
    assert manager.count_descendants(3) == 0


def test_update_population_totals_bottom_up():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "population": 1},
            "3": {"node_id": 3, "parent_id": 2, "children": [4, 5]},
            "4": {"node_id": 4, "parent_id": 3, "children": [], "population": 4},
            "5": {"node_id": 5, "parent_id": 3, "children": [], "free_peasants": 2},
        },
        "characters": {},
    }

    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: {1: 0, 2: 1, 3: 2, 4: 3, 5: 3}[nid]
    manager.update_population_totals()

    assert world["nodes"]["5"]["population"] == 2
    assert world["nodes"]["3"]["population"] == 6
    assert world["nodes"]["2"]["population"] == 7
    assert world["nodes"]["1"]["population"] == 7


def test_population_totals_after_subfief_changes():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "num_subfiefs": 1},
            "3": {"node_id": 3, "parent_id": 2, "children": [], "population": 5},
        },
        "next_node_id": 4,
        "characters": {},
    }

    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: {1: 0, 2: 1, 3: 2, 4: 2}.get(nid, 2)

    manager.update_population_totals()
    assert world["nodes"]["2"]["population"] == 5
    assert world["nodes"]["1"]["population"] == 5

    node2 = world["nodes"]["2"]
    node2["num_subfiefs"] = 2
    manager.update_subfiefs_for_node(node2)
    new_id = node2["children"][-1]
    world["nodes"][str(new_id)]["population"] = 3

    manager.update_population_totals()
    assert world["nodes"][str(new_id)]["population"] == 3
    assert world["nodes"]["2"]["population"] == 8
    assert world["nodes"]["1"]["population"] == 8

    node2["num_subfiefs"] = 1
    manager.update_subfiefs_for_node(node2)

    manager.update_population_totals()
    assert str(new_id) not in world["nodes"]
    assert world["nodes"]["2"]["population"] == 5
    assert world["nodes"]["1"]["population"] == 5


def test_population_totals_refresh_after_edit():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [], "free_peasants": 3},
        },
        "characters": {},
    }

    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: {1: 0, 2: 1}[nid]

    manager.update_population_totals()
    assert world["nodes"]["2"]["population"] == 3
    assert world["nodes"]["1"]["population"] == 3

    # Modify settlement data on node 2
    world["nodes"]["2"]["free_peasants"] = 5

    manager.update_population_totals()
    assert world["nodes"]["2"]["population"] == 5
    assert world["nodes"]["1"]["population"] == 5


def test_set_border_between_updates_both_nodes():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "neighbors": [{"id": 2, "border": NEIGHBOR_NONE_STR}] + [{"id": None, "border": NEIGHBOR_NONE_STR}] * (MAX_NEIGHBORS - 1),
            },
            "2": {
                "node_id": 2,
                "parent_id": None,
                "neighbors": [{"id": 1, "border": NEIGHBOR_NONE_STR}] + [{"id": None, "border": NEIGHBOR_NONE_STR}] * (MAX_NEIGHBORS - 1),
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)

    changed = manager.set_border_between(1, 2, "v\u00e4g")
    assert changed
    assert world["nodes"]["1"]["neighbors"][0]["border"] == "v\u00e4g"
    assert world["nodes"]["2"]["neighbors"][0]["border"] == "v\u00e4g"

    changed = manager.set_border_between(1, 2, "v\u00e4g")
    assert not changed

    changed = manager.set_border_between(1, 2, "bogus")
    assert changed
    assert world["nodes"]["1"]["neighbors"][0]["border"] == NEIGHBOR_NONE_STR
    assert world["nodes"]["2"]["neighbors"][0]["border"] == NEIGHBOR_NONE_STR


def test_population_totals_use_parent_links():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [4]},
            "4": {"node_id": 4, "parent_id": 1, "children": [], "res_type": "Gods"},
            "5": {
                "node_id": 5,
                "parent_id": 4,
                "children": [],
                "res_type": "Bosättning",
                "free_peasants": 6,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    manager.get_depth_of_node = lambda nid: {1: 0, 4: 1, 5: 2}[nid]

    manager.update_population_totals()

    assert world["nodes"]["5"]["population"] == 6
    assert world["nodes"]["4"]["population"] == 6
    assert world["nodes"]["1"]["population"] == 6


def test_update_subfiefs_skips_weather_nodes():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "res_type": "Väder",
                "num_subfiefs": 3,
            }
        },
        "characters": {},
    }

    manager = WorldManager(world)
    manager.update_subfiefs_for_node(world["nodes"]["1"])

    assert world["nodes"]["1"]["children"] == []
    assert world["nodes"]["1"]["num_subfiefs"] == 0


def test_calculate_work_available_excludes_other_jarldoms():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2, 3],
                "thralls": 1,
                "unfree_peasants": 1,
                "dagsverken": "normalt",
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [4],
                "unfree_peasants": 2,
                "dagsverken": "många",
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "children": [],
                "thralls": 1,
                "dagsverken": "få",
            },
            "4": {
                "node_id": 4,
                "parent_id": 2,
                "children": [],
                "unfree_peasants": 1,
                "dagsverken": "inga",
            },
            "5": {
                "node_id": 5,
                "parent_id": None,
                "children": [],
                "thralls": 10,
                "unfree_peasants": 10,
                "dagsverken": "många",
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_work_available(1)
    expected = (
        THRALL_WORK_DAYS
        + DAGSVERKEN_MULTIPLIERS["normalt"]
        + DAGSVERKEN_MULTIPLIERS["många"] * 2
        + THRALL_WORK_DAYS
        + DAGSVERKEN_MULTIPLIERS["inga"]
    )
    assert total == expected


def test_calculate_work_available_includes_day_laborers():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "day_laborers_hired": 2,
            }
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_work_available(1)
    assert total == DAY_LABORER_WORK_DAYS * 2


def test_calculate_umbarande_excludes_other_jarldoms():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2, 3],
                "dagsverken": "normalt",
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [4],
                "dagsverken": "många",
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "children": [],
                "dagsverken": "få",
            },
            "4": {
                "node_id": 4,
                "parent_id": 2,
                "children": [],
                "dagsverken": "inga",
            },
            "5": {
                "node_id": 5,
                "parent_id": None,
                "children": [],
                "dagsverken": "tyranniskt många",
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_umbarande(1)
    expected = (
        DAGSVERKEN_UMBARANDE["normalt"]
        + DAGSVERKEN_UMBARANDE["många"]
        + DAGSVERKEN_UMBARANDE["få"]
        + DAGSVERKEN_UMBARANDE["inga"]
    )
    assert total == expected


def test_calculate_umbarande_includes_weather_effect():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2],
                "dagsverken": "normalt",
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "res_type": "Väder",
                "weather_effect": 5,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_umbarande(1)
    expected = DAGSVERKEN_UMBARANDE["normalt"] + 5
    assert total == expected


def test_calculate_license_income_sums_descendants():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2, 3],
                "expected_license_income": 1,
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [4],
                "expected_license_income": 2,
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "children": [],
                "expected_license_income": 3,
            },
            "4": {
                "node_id": 4,
                "parent_id": 2,
                "children": [],
                "expected_license_income": 4,
            },
            "5": {
                "node_id": 5,
                "parent_id": None,
                "children": [],
                "expected_license_income": 100,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_license_income(1)
    assert total == 1 + 2 + 3 + 4
