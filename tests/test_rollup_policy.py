import copy

from src.constants import THRALL_WORK_DAYS
from src.rollup_policy import (
    get_local_population_contribution,
    get_local_work_needed_contribution,
)


def test_local_population_contribution_uses_population_categories():
    node = {"free_peasants": 6}

    assert get_local_population_contribution(node) == 6


def test_summary_node_population_is_not_a_local_contribution():
    node = {"res_type": "Gods", "population": 6, "children": [2]}

    assert get_local_population_contribution(node) == 0


def test_local_population_contribution_uses_base_population_fallback():
    node = {"_base_population": 4}

    assert get_local_population_contribution(node) == 4


def test_local_population_contribution_does_not_mutate_node():
    node = {"free_peasants": 6, "children": [2]}
    original = copy.deepcopy(node)

    get_local_population_contribution(node)

    assert node == original


def test_local_population_contribution_handles_missing_values():
    assert get_local_population_contribution({}) == 0


def test_local_population_contribution_handles_invalid_values_safely():
    node = {
        "free_peasants": "invalid",
        "unfree_peasants": -2,
        "thralls": None,
        "burghers": 3,
    }

    assert get_local_population_contribution(node) == 3


def test_low_level_reported_population_is_not_a_local_contribution():
    node = {"level": 3, "population": 6}

    assert get_local_population_contribution(node) == 0


def test_local_work_needed_contribution_uses_resource_need():
    assert get_local_work_needed_contribution({"work_needed": 25}, depth=4) == 25


def test_local_work_needed_contribution_ignores_level_three_report_total():
    assert get_local_work_needed_contribution({"work_needed": 100}, depth=3) == 0


def test_local_work_needed_contribution_uses_fishing_boats_for_water():
    for res_type in ("Hav", "Flod"):
        node = {
            "res_type": res_type,
            "fishing_boats": 2,
            "work_needed": 999,
        }

        assert get_local_work_needed_contribution(node, depth=4) == 2 * THRALL_WORK_DAYS


def test_local_work_needed_contribution_does_not_mutate_node():
    node = {"work_needed": 25, "children": [2]}
    original = copy.deepcopy(node)

    get_local_work_needed_contribution(node, depth=4)

    assert node == original


def test_local_work_needed_contribution_handles_invalid_values_safely():
    assert get_local_work_needed_contribution({}, depth=4) == 0
    assert get_local_work_needed_contribution({"work_needed": "invalid"}, depth=4) == 0
    assert get_local_work_needed_contribution({"work_needed": -25}, depth=4) == 0
    assert (
        get_local_work_needed_contribution(
            {"res_type": "Hav", "fishing_boats": -2}, depth=4
        )
        == 0
    )


def test_local_work_needed_contribution_uses_node_depth_fallback():
    assert get_local_work_needed_contribution({"depth": 4, "work_needed": 25}) == 25
    assert get_local_work_needed_contribution({"level": 3, "work_needed": 25}) == 0
    assert get_local_work_needed_contribution({"work_needed": 25}) == 0
