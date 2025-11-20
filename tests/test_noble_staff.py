from noble_staff import (
    NOBLE_BUILDING_ORDER,
    NOBLE_STANDARD_ORDER,
    STAFF_ROLE_ORDER,
    calculate_noble_household,
    calculate_staff_costs,
    calculate_staff_cost_totals,
    calculate_staff_requirements,
    get_housing_requirement_for_level,
    get_highest_building_rank,
    get_living_level_for_standard,
    get_max_allowed_standard_for_buildings,
)


def test_living_level_mapping_and_housing_requirement():
    assert get_living_level_for_standard("Enkel") == "Nödtorftig"
    assert get_living_level_for_standard("Furstlig") == "Lyxliv"
    assert get_living_level_for_standard(None) == "God"
    assert get_housing_requirement_for_level("Lyxliv") == "Sammansatt borgkärna"


def test_noble_standard_and_building_order_match_spec():
    assert NOBLE_STANDARD_ORDER == (
        "Enkel",
        "Anständig",
        "Välbärgad",
        "Förnäm",
        "Furstlig",
    )
    assert NOBLE_BUILDING_ORDER == (
        "Trästuga liten",
        "Trästuga 2 våningar",
        "Stenhus",
        "Borgkärna",
        "Sammansatt borgkärna",
    )


def test_building_types_map_to_correct_noble_standard():
    for building, standard in zip(NOBLE_BUILDING_ORDER, NOBLE_STANDARD_ORDER):
        allowed = get_max_allowed_standard_for_buildings(
            [{"type": building, "count": 1}]
        )
        assert (
            allowed == standard
        ), f"{building} ska maximalt stödja {standard}, fick {allowed}"


def test_get_highest_building_rank_defaults_missing_counts():
    rank = get_highest_building_rank([
        {"type": "Stenhus", "count": ""},
        {"type": "Borgkärna"},
    ])

    assert rank == 3


def test_staff_roles_are_ordered_by_seniority():
    expected_order = (
        "Kammarherre",
        "Hovmästare",
        "Köksmästare",
        "Kock",
        "Kammarjungfru",
        "Kallskänka",
        "Kokerka",
        "Tjänare",
        "Hushållspersonal",
    )
    assert STAFF_ROLE_ORDER == expected_order


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


def test_staff_base_and_lyx_cost_totals():
    counts = {"Kammarherre": 2, "Kock": 3, "Tjänare": 0}
    cost_totals, base_total, lyx_total = calculate_staff_cost_totals(counts)

    assert cost_totals["Kammarherre"] == (4, 4)
    assert cost_totals["Kock"] == (9, None)
    assert base_total == 13
    assert lyx_total == 4
