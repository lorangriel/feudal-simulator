import copy

from src.rollup_policy import get_local_population_contribution


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
