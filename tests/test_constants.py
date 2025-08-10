"""Tests for global constants to ensure they match expected values and remain unchanged."""

from copy import deepcopy

from src import constants


def test_basic_constant_values():
    """Basic immutable constants should match expected default values."""
    assert constants.DEFAULT_WORLDS_FILE == "worlds.json"
    assert constants.DEFAULT_BORDER_TYPE == "vildmark"
    assert constants.NEIGHBOR_NONE_STR == "<Ingen>"
    assert constants.NEIGHBOR_OTHER_STR == "Annat land"
    assert constants.MAX_NEIGHBORS == 6
    assert constants.THRALL_WORK_DAYS == 300
    assert constants.DAY_LABORER_WORK_DAYS == 70
    assert constants.MAX_FISHING_BOATS == 20


def test_border_types_not_mutated():
    """Modifying a copy of BORDER_TYPES must not alter the original constant."""
    expected = [
        "<Ingen>",
        "liten väg",
        "väg",
        "stor väg",
        "vildmark",
        "träsk",
        "berg",
        "vattendrag",
    ]
    assert constants.BORDER_TYPES == expected

    local_copy = constants.BORDER_TYPES[:]
    local_copy.append("ny gräns")
    assert constants.BORDER_TYPES == expected


def test_res_types_not_mutated():
    """The list of resource types should keep its original contents."""
    assert constants.RES_TYPES[0] == "Resurs"
    assert "Officer" in constants.RES_TYPES

    local_copy = constants.RES_TYPES[:]
    local_copy.append("Ny resurs")
    assert constants.RES_TYPES[-1] != "Ny resurs"


def test_craftsman_types_and_fees_consistency():
    """Craftsman types mirror the license fee keys and stay unchanged."""
    expected_types = list(constants.CRAFTSMAN_LICENSE_FEES.keys())
    assert constants.CRAFTSMAN_TYPES == expected_types
    assert constants.CRAFTSMAN_LICENSE_FEES["Båtbyggare"] == 200

    fees_copy = deepcopy(constants.CRAFTSMAN_LICENSE_FEES)
    fees_copy["Testare"] = 1
    assert "Testare" not in constants.CRAFTSMAN_LICENSE_FEES

    types_copy = constants.CRAFTSMAN_TYPES[:]
    types_copy.append("Testare")
    assert "Testare" not in constants.CRAFTSMAN_TYPES


def test_dagsverken_levels_and_multipliers():
    """Dagsverken level data should not be accidentally modified."""
    expected_levels = ["inga", "få", "normalt", "många", "tyranniskt många"]
    assert constants.DAGSVERKEN_LEVELS == expected_levels
    assert constants.DAGSVERKEN_MULTIPLIERS["inga"] == 0
    assert constants.DAGSVERKEN_UMBARANDE["tyranniskt många"] == 2

    levels_copy = constants.DAGSVERKEN_LEVELS[:]
    levels_copy.append("extra nivå")
    assert constants.DAGSVERKEN_LEVELS == expected_levels

    multipliers_copy = deepcopy(constants.DAGSVERKEN_MULTIPLIERS)
    multipliers_copy["extra nivå"] = 999
    assert "extra nivå" not in constants.DAGSVERKEN_MULTIPLIERS
