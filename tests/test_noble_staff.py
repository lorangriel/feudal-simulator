from noble_staff import (
    STAFF_ROLE_ORDER,
    calculate_noble_household,
    calculate_staff_costs,
    calculate_staff_requirements,
    get_housing_requirement_for_level,
    get_living_level_for_standard,
)


def test_living_level_mapping_and_housing_requirement():
    assert get_living_level_for_standard("Enkel") == "Nödtorftig"
    assert get_living_level_for_standard("Furstlig") == "Lyxliv"
    assert get_living_level_for_standard(None) == "God"
    assert get_housing_requirement_for_level("Lyxliv") == "Sammansatt borgkärna"


def test_calculate_noble_household_counts_entries():
    node_data = {
        "noble_lord": {"kind": "character", "char_id": 1},
        "noble_spouses": [
            {"kind": "character", "char_id": 2},
            {"kind": "placeholder", "label": "Partner"},
            {"kind": "placeholder", "label": ""},
        ],
        "noble_spouse_children": [
            [
                {"kind": "placeholder", "label": "Barn levande"},
                {"kind": "character", "char_id": 3},
                {"kind": "placeholder", "label": ""},
            ]
        ],
        "noble_relatives": [
            {"kind": "character", "char_id": 4},
            5,
            " ",
        ],
    }
    summary = calculate_noble_household(node_data)
    assert summary.lord == 1
    assert summary.spouses == 2
    assert summary.children == 2
    assert summary.relatives == 2
    assert summary.total == 7


def test_staff_requirements_for_gemen_level():
    counts = calculate_staff_requirements("Gemen", 10)
    assert counts["Kokerka"] == 1
    assert counts["Tjänare"] == 1
    assert counts["Hushållspersonal"] == 2
    assert counts["Kallskänka"] == 1
    for role in STAFF_ROLE_ORDER:
        if role not in {"Kokerka", "Tjänare", "Hushållspersonal", "Kallskänka"}:
            assert counts[role] == 0


def test_staff_requirements_and_costs_for_lyxliv():
    counts = calculate_staff_requirements("Lyxliv", 8)
    assert counts["Tjänare"] == 19
    assert counts["Hushållspersonal"] == 26
    assert "Kammarjungfru" in counts
    assert counts["Kammarjungfru"] == 7
    assert counts["Kallskänka"] == 5
    assert counts["Kokerka"] == 7
    assert counts["Kock"] == 1
    assert counts["Kammarherre"] == 1
    assert counts["Hovmästare"] == 1
    assert counts["Köksmästare"] == 1

    cost_map, total = calculate_staff_costs(counts, "Lyxliv")
    assert cost_map["Köksmästare"] == (1, 1)
    assert cost_map["Kammarherre"] == (2, 2)
    assert total >= 1
