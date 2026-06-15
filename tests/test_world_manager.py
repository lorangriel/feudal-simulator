import copy

from src.world_manager import WorldManager
from src.constants import (
    MAX_NEIGHBORS,
    NEIGHBOR_NONE_STR,
    DAGSVERKEN_MULTIPLIERS,
    THRALL_WORK_DAYS,
    DAGSVERKEN_UMBARANDE,
    DAY_LABORER_WORK_DAYS,
)
from src.rollup_policy import STORAGE_RESOURCE_KEYS


def _storage_node(node_id, parent_id=None, children=None, res_type=None, **values):
    return {
        "node_id": node_id,
        "parent_id": parent_id,
        "children": children or [],
        "res_type": res_type,
        **values,
    }


def _storage_manager(*nodes):
    return WorldManager(
        {"nodes": {str(node["node_id"]): node for node in nodes}, "characters": {}}
    )


def test_get_storage_report_returns_all_storage_keys():
    report = _storage_manager().get_storage_report(999)

    assert set(report) == set(STORAGE_RESOURCE_KEYS)
    assert all(value == 0 for value in report.values())


def test_get_storage_report_counts_direct_lager_child():
    manager = _storage_manager(
        _storage_node(1, children=[2], res_type="Jarldöme"),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_counts_nested_lager_under_estate():
    manager = _storage_manager(
        _storage_node(1, children=[2], res_type="Jarldöme"),
        _storage_node(2, 1, [3], "Gods"),
        _storage_node(3, 2, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_counts_multiple_lager_nodes():
    manager = _storage_manager(
        _storage_node(1, children=[2, 3]),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
        _storage_node(3, 1, res_type="Lager", storage_basic=5),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 12


def test_get_storage_report_supports_all_storage_keys():
    values = {key: index for index, key in enumerate(STORAGE_RESOURCE_KEYS, 1)}
    manager = _storage_manager(_storage_node(1, res_type="Lager", **values))

    assert manager.get_storage_report(1) == values


def test_get_storage_report_ignores_jarldom_storage_fields():
    manager = _storage_manager(
        _storage_node(1, children=[2], res_type="Jarldöme", storage_basic=100),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_ignores_estate_storage_fields():
    manager = _storage_manager(
        _storage_node(1, children=[2]),
        _storage_node(2, 1, [3], "Gods", storage_basic=100),
        _storage_node(3, 2, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_ignores_settlement_storage_fields():
    manager = _storage_manager(
        _storage_node(1, children=[2]),
        _storage_node(2, 1, [3], "By", storage_basic=100),
        _storage_node(3, 2, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_counts_start_node_if_it_is_lager():
    manager = _storage_manager(_storage_node(1, res_type="Lager", storage_basic=7))

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_handles_missing_node():
    report = _storage_manager().get_storage_report("missing")

    assert report == {key: 0 for key in STORAGE_RESOURCE_KEYS}


def test_get_storage_report_handles_invalid_child_ids():
    manager = _storage_manager(_storage_node(1, children=["invalid"]))

    assert manager.get_storage_report(1) == {key: 0 for key in STORAGE_RESOURCE_KEYS}


def test_get_storage_report_counts_duplicate_child_reference_once():
    manager = _storage_manager(
        _storage_node(1, children=[2, 2]),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_stops_at_cycles():
    manager = _storage_manager(
        _storage_node(1, 2, [2], "Lager", storage_basic=3),
        _storage_node(2, 1, [1], "Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 10


def test_get_storage_report_includes_parent_id_child():
    manager = _storage_manager(
        _storage_node(1),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
    )

    assert manager.get_storage_report(1)["storage_basic"] == 7


def test_get_storage_report_does_not_mutate_world_data():
    manager = _storage_manager(
        _storage_node(1, children=[2]),
        _storage_node(2, 1, res_type="Lager", storage_basic=7),
    )
    original = copy.deepcopy(manager.world_data)

    manager.get_storage_report(1)

    assert manager.world_data == original


def test_get_storage_report_does_not_write_total_resources():
    manager = _storage_manager(_storage_node(1))

    manager.get_storage_report(1)

    assert "total_resources" not in manager.world_data["nodes"]["1"]


def test_get_storage_report_does_not_write_storage_fields():
    manager = _storage_manager(_storage_node(1, res_type="Lager"))
    original = copy.deepcopy(manager.world_data["nodes"]["1"])

    manager.get_storage_report(1)

    assert manager.world_data["nodes"]["1"] == original


def test_attempt_link_neighbors_directional():
    world = {
        "nodes": {
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
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda _nid: 3

    ok, _ = manager.attempt_link_neighbors(10, 20, slot1=2)
    assert ok
    assert world["nodes"]["10"]["neighbors"][1]["id"] == 20
    assert world["nodes"]["20"]["neighbors"][4]["id"] == 10


def test_attempt_link_neighbors_preserves_existing_links():
    world = {
        "nodes": {
            "10": {
                "node_id": 10,
                "parent_id": 1,
                "neighbors": [{"id": 30, "border": NEIGHBOR_NONE_STR}]
                + [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - 1)
                ],
            },
            "20": {
                "node_id": 20,
                "parent_id": 1,
                "neighbors": [{"id": 40, "border": NEIGHBOR_NONE_STR}]
                + [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - 1)
                ],
            },
            "30": {
                "node_id": 30,
                "parent_id": 1,
                "neighbors": [{"id": 10, "border": NEIGHBOR_NONE_STR}]
                + [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - 1)
                ],
            },
            "40": {
                "node_id": 40,
                "parent_id": 1,
                "neighbors": [{"id": 20, "border": NEIGHBOR_NONE_STR}]
                + [
                    {"id": None, "border": NEIGHBOR_NONE_STR}
                    for _ in range(MAX_NEIGHBORS - 1)
                ],
            },
        },
        "characters": {},
    }
    manager = WorldManager(world)
    manager.get_depth_of_node = lambda _nid: 3

    ok, _ = manager.attempt_link_neighbors(10, 20)
    assert ok
    # existing neighbor links remain
    assert world["nodes"]["10"]["neighbors"][0]["id"] == 30
    assert world["nodes"]["20"]["neighbors"][0]["id"] == 40
    assert world["nodes"]["30"]["neighbors"][0]["id"] == 10
    assert world["nodes"]["40"]["neighbors"][0]["id"] == 20
    # new link created without affecting other slots
    assert any(nb["id"] == 20 for nb in world["nodes"]["10"]["neighbors"])
    assert any(nb["id"] == 10 for nb in world["nodes"]["20"]["neighbors"])


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

    assert totals["population"] == 9
    assert totals["soldiers"]["Archer"] == 3
    assert world["nodes"]["2"]["total_resources"]["population"] == 2
    assert world["nodes"]["4"]["total_resources"]["population"] == 2


def test_calculate_total_resources_cycle():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [1],  # cycle back to root
                "_base_population": 5,
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


def _population_world(direct_population=None, estate_population=None):
    nodes = {
        "1": {"node_id": 1, "parent_id": None, "children": []},
    }
    if direct_population is not None:
        nodes["2"] = {
            "node_id": 2,
            "parent_id": 1,
            "children": [],
            "res_type": "Bosättning",
            "free_peasants": direct_population,
        }
        nodes["1"]["children"].append(2)
    if estate_population is not None:
        nodes["3"] = {
            "node_id": 3,
            "parent_id": 1,
            "children": [4],
            "res_type": "Gods",
            "population": estate_population,
        }
        nodes["4"] = {
            "node_id": 4,
            "parent_id": 3,
            "children": [],
            "res_type": "Bosättning",
            "free_peasants": 6,
        }
        nodes["1"]["children"].append(3)
    return {"nodes": nodes, "characters": {}}


def test_population_rollup_counts_direct_village_once():
    manager = WorldManager(_population_world(direct_population=6))

    assert manager.calculate_total_resources(1)["population"] == 6


def test_population_rollup_counts_village_under_estate_once():
    manager = WorldManager(_population_world(estate_population=0))

    assert manager.calculate_total_resources(1)["population"] == 6


def test_population_rollup_ignores_estate_report_value():
    manager = WorldManager(_population_world(estate_population=6))

    assert manager.calculate_total_resources(1)["population"] == 6


def test_population_rollup_counts_each_source_node_once():
    manager = WorldManager(_population_world(direct_population=4, estate_population=6))

    assert manager.calculate_total_resources(1)["population"] == 10


def test_population_rollup_counts_node_reached_by_both_links_once():
    world = _population_world(direct_population=6)
    world["nodes"]["1"]["children"] = []

    manager = WorldManager(world)

    assert manager.calculate_total_resources(1)["population"] == 6


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
                "neighbors": [{"id": 2, "border": NEIGHBOR_NONE_STR}]
                + [{"id": None, "border": NEIGHBOR_NONE_STR}] * (MAX_NEIGHBORS - 1),
            },
            "2": {
                "node_id": 2,
                "parent_id": None,
                "neighbors": [{"id": 1, "border": NEIGHBOR_NONE_STR}]
                + [{"id": None, "border": NEIGHBOR_NONE_STR}] * (MAX_NEIGHBORS - 1),
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


def test_calculate_work_available_still_ignores_stored_report_total():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "work_available": 999,
                "work_needed": 999,
            }
        },
        "characters": {},
    }

    assert WorldManager(world).calculate_work_available(1) == 0


def test_calculate_work_available_counts_duplicate_child_reference_once():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2, 2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "thralls": 1,
            },
        },
        "characters": {},
    }

    assert WorldManager(world).calculate_work_available(1) == THRALL_WORK_DAYS


def test_calculate_work_available_stops_at_cycles():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2],
                "thralls": 1,
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [1],
                "thralls": 1,
            },
        },
        "characters": {},
    }

    assert WorldManager(world).calculate_work_available(1) == 2 * THRALL_WORK_DAYS


def test_calculate_work_available_keeps_explicit_people_on_upper_level():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "thralls": 1,
                "unfree_peasants": 2,
                "dagsverken": "normalt",
            }
        },
        "characters": {},
    }

    expected = THRALL_WORK_DAYS + 2 * DAGSVERKEN_MULTIPLIERS["normalt"]
    assert WorldManager(world).calculate_work_available(1) == expected


def test_calculate_work_available_treats_same_village_equally_under_estate():
    direct_world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "thralls": 1,
                "unfree_peasants": 2,
            },
        },
        "characters": {},
    }
    estate_world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [3],
                "res_type": "Gods",
            },
            "3": {
                "node_id": 3,
                "parent_id": 2,
                "children": [],
                "thralls": 1,
                "unfree_peasants": 2,
            },
        },
        "characters": {},
    }

    direct_total = WorldManager(direct_world).calculate_work_available(1)
    estate_total = WorldManager(estate_world).calculate_work_available(1)

    assert estate_total == direct_total


def test_calculate_work_available_still_ignores_available_day_laborers():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "day_laborers_available": 10,
            }
        },
        "characters": {},
    }

    assert WorldManager(world).calculate_work_available(1) == 0


def test_calculate_work_available_documents_duplicate_person_model_risk():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2],
                "thralls": 1,
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "thralls": 1,
            },
        },
        "characters": {},
    }

    # Current traversal counts both explicit values; their provenance is unresolved.
    assert WorldManager(world).calculate_work_available(1) == 2 * THRALL_WORK_DAYS


def _work_world(nodes):
    return {"nodes": {str(node["node_id"]): node for node in nodes}, "characters": {}}


def test_calculate_work_available_counts_depth_three_local_thralls():
    nodes = [
        {
            "node_id": i,
            "parent_id": i - 1 if i > 1 else None,
            "children": [i + 1] if i < 4 else [],
        }
        for i in range(1, 5)
    ]
    nodes[3]["thralls"] = 2

    assert (
        WorldManager(_work_world(nodes)).calculate_work_available(4)
        == 2 * THRALL_WORK_DAYS
    )


def test_calculate_work_available_counts_depth_three_local_unfree_peasants():
    node = {
        "node_id": 1,
        "parent_id": None,
        "children": [],
        "unfree_peasants": 2,
        "dagsverken": "många",
    }
    manager = WorldManager(_work_world([node]))
    manager.get_depth_of_node = lambda _node_id: 3

    assert manager.calculate_work_available(1) == 2 * DAGSVERKEN_MULTIPLIERS["många"]


def test_calculate_work_available_counts_depth_three_hired_day_laborers_with_children():
    parent = {"node_id": 1, "parent_id": None, "children": [2], "day_laborers_hired": 2}
    child = {"node_id": 2, "parent_id": 1, "children": [], "thralls": 1}

    assert (
        WorldManager(_work_world([parent, child])).calculate_work_available(1)
        == 2 * DAY_LABORER_WORK_DAYS + THRALL_WORK_DAYS
    )


def test_calculate_work_available_counts_estate_local_people_and_child_people():
    estate = {
        "node_id": 1,
        "parent_id": None,
        "children": [2],
        "res_type": "Gods",
        "thralls": 1,
    }
    child = {"node_id": 2, "parent_id": 1, "children": [], "unfree_peasants": 2}
    expected = THRALL_WORK_DAYS + 2 * DAGSVERKEN_MULTIPLIERS["normalt"]

    assert (
        WorldManager(_work_world([estate, child])).calculate_work_available(1)
        == expected
    )


def test_calculate_work_available_uses_each_nodes_own_dagsverken():
    parent = {
        "node_id": 1,
        "parent_id": None,
        "children": [2],
        "unfree_peasants": 1,
        "dagsverken": "få",
    }
    child = {
        "node_id": 2,
        "parent_id": 1,
        "children": [],
        "unfree_peasants": 1,
        "dagsverken": "många",
    }
    expected = DAGSVERKEN_MULTIPLIERS["få"] + DAGSVERKEN_MULTIPLIERS["många"]

    assert (
        WorldManager(_work_world([parent, child])).calculate_work_available(1)
        == expected
    )


def test_calculate_work_available_uses_normal_for_invalid_dagsverken():
    node = {
        "node_id": 1,
        "parent_id": None,
        "children": [],
        "unfree_peasants": 2,
        "dagsverken": "invalid",
    }

    assert (
        WorldManager(_work_world([node])).calculate_work_available(1)
        == 2 * DAGSVERKEN_MULTIPLIERS["normalt"]
    )


def test_calculate_work_available_clamps_negative_local_people():
    node = {
        "node_id": 1,
        "parent_id": None,
        "children": [],
        "thralls": -1,
        "unfree_peasants": -2,
        "day_laborers_hired": -3,
    }

    assert WorldManager(_work_world([node])).calculate_work_available(1) == 0


def test_calculate_work_available_does_not_mutate_nodes():
    world = _work_world(
        [{"node_id": 1, "parent_id": None, "children": [], "thralls": 1}]
    )
    original = copy.deepcopy(world)

    WorldManager(world).calculate_work_available(1)

    assert world == original


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


def test_calculate_work_needed_counts_fishing_boats():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2],
                "work_needed": 50,
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [],
                "res_type": "Hav",
                "fishing_boats": 3,
            },
        },
        "characters": {},
    }

    manager = WorldManager(world)
    total = manager.calculate_work_needed(1)
    assert total == 3 * THRALL_WORK_DAYS


def _work_needed_world(jarldom_work=0, child_needs=(10,)):
    nodes = {
        "1": {"node_id": 1, "parent_id": None, "children": [2]},
        "2": {"node_id": 2, "parent_id": 1, "children": [3]},
        "3": {"node_id": 3, "parent_id": 2, "children": [4]},
        "4": {
            "node_id": 4,
            "parent_id": 3,
            "children": list(range(5, 5 + len(child_needs))),
            "work_needed": jarldom_work,
        },
    }
    for node_id, work_needed in enumerate(child_needs, start=5):
        nodes[str(node_id)] = {
            "node_id": node_id,
            "parent_id": 4,
            "children": [],
            "work_needed": work_needed,
        }
    return {"nodes": nodes, "characters": {}}


def test_update_work_needed_does_not_recount_stored_jarldom_total():
    world = _work_needed_world(child_needs=(10,))
    manager = WorldManager(world)

    assert manager.update_work_needed(4) == 10
    assert manager.update_work_needed(4) == 10
    assert world["nodes"]["4"]["work_needed"] == 10


def test_calculate_work_needed_ignores_stored_jarldom_report_total():
    manager = WorldManager(_work_needed_world(jarldom_work=100, child_needs=(10,)))

    assert manager.calculate_work_needed(4) == 10


def test_calculate_work_needed_sums_each_local_resource_once():
    manager = WorldManager(_work_needed_world(child_needs=(10, 20)))

    assert manager.calculate_work_needed(4) == 30


def test_calculate_work_needed_keeps_water_fishing_boat_need():
    world = _work_needed_world(child_needs=(999,))
    world["nodes"]["5"].update({"res_type": "Flod", "fishing_boats": 2})
    manager = WorldManager(world)

    assert manager.calculate_work_needed(4) == 2 * THRALL_WORK_DAYS


def test_calculate_work_needed_counts_duplicate_child_reference_once():
    world = _work_needed_world(child_needs=(10,))
    world["nodes"]["4"]["children"] = [5, 5]
    manager = WorldManager(world)

    assert manager.calculate_work_needed(4) == 10


def test_calculate_work_needed_stops_at_cycles():
    world = _work_needed_world(child_needs=(10,))
    world["nodes"]["5"]["children"] = [4]
    manager = WorldManager(world)

    assert manager.calculate_work_needed(4) == 10


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
