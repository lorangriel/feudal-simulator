import copy

from world_relations import (
    RelationIssue,
    clear_jarldom_owner,
    clear_title_seat,
    get_jarldom_owner,
    get_owned_jarldoms,
    get_seated_title,
    get_title_seat,
    set_jarldom_owner,
    set_title_seat,
    validate_world_relations,
)


def make_world():
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {"node_id": 2, "parent_id": 1},
            "3": {"node_id": 3, "parent_id": 2},
            "4": {"node_id": 4, "parent_id": 3},
            "5": {"node_id": 5, "parent_id": 1},
            "6": {"node_id": 6, "parent_id": 5},
            "7": {"node_id": 7, "parent_id": 6},
            "8": {"node_id": 8, "parent_id": 4},
        },
        "characters": {"10": {"name": "Owner"}, "11": {"name": "Other"}},
    }


def issue_codes(world_data, strict=False):
    return {issue.code for issue in validate_world_relations(world_data, strict=strict)}


def test_missing_relation_indexes_are_empty_without_mutation():
    world_data = make_world()
    original = copy.deepcopy(world_data)

    assert get_title_seat(world_data, 1) is None
    assert get_seated_title(world_data, 4) is None
    assert get_jarldom_owner(world_data, 4) is None
    assert get_owned_jarldoms(world_data, 10) == []
    assert validate_world_relations(world_data) == []
    assert world_data == original


def test_relation_queries_accept_string_encoded_ids():
    world_data = make_world()
    world_data["title_seats"] = {"1": "4"}
    world_data["jarldom_owners"] = {"4": "10"}

    assert get_title_seat(world_data, "1") == 4
    assert get_seated_title(world_data, "4") == 1
    assert get_jarldom_owner(world_data, "4") == 10
    assert get_owned_jarldoms(world_data, "10") == [4]


def test_unknown_top_level_data_is_untouched():
    world_data = make_world()
    world_data["future_data"] = {"nested": [1, 2, 3]}
    original = copy.deepcopy(world_data)

    validate_world_relations(world_data, strict=True)

    assert world_data == original


def test_get_title_seat_returns_level_three_descendant():
    world_data = make_world()
    world_data["title_seats"] = {"2": "4"}

    assert get_title_seat(world_data, 2) == 4


def test_get_seated_title_returns_unique_title():
    world_data = make_world()
    world_data["title_seats"] = {"2": "4"}

    assert get_seated_title(world_data, 4) == 2


def test_get_seated_title_returns_none_for_duplicate_seat():
    world_data = make_world()
    world_data["title_seats"] = {"1": "4", "2": "4"}

    assert get_seated_title(world_data, 4) is None


def test_validation_reports_title_without_seat_in_strict_mode():
    world_data = make_world()

    assert "title_missing_seat" not in issue_codes(world_data)
    assert "title_missing_seat" in issue_codes(world_data, strict=True)


def test_validation_reports_unknown_title_node():
    world_data = make_world()
    world_data["title_seats"] = {"999": "4"}

    assert "unknown_title_node" in issue_codes(world_data)


def test_validation_reports_non_title_source():
    world_data = make_world()
    world_data["title_seats"] = {"4": "7"}

    assert "seat_source_not_title" in issue_codes(world_data)


def test_validation_reports_unknown_seat_node():
    world_data = make_world()
    world_data["title_seats"] = {"2": "999"}

    assert "unknown_seat_node" in issue_codes(world_data)


def test_validation_reports_non_jarldom_seat():
    world_data = make_world()
    world_data["title_seats"] = {"1": "3", "2": "8"}

    assert "seat_not_jarldom" in issue_codes(world_data)


def test_validation_reports_seat_outside_title_subtree():
    world_data = make_world()
    world_data["title_seats"] = {"2": "7"}

    assert "seat_outside_title_subtree" in issue_codes(world_data)


def test_validation_reports_duplicate_seat():
    world_data = make_world()
    world_data["title_seats"] = {"1": "4", "2": "4"}

    issues = validate_world_relations(world_data)

    assert [issue.code for issue in issues].count("duplicate_title_seat") == 2


def test_get_jarldom_owner_returns_existing_character():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "10"}

    assert get_jarldom_owner(world_data, 4) == 10


def test_get_owned_jarldoms_returns_multiple_jarldoms_for_same_character():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "10", "7": 10}

    assert get_owned_jarldoms(world_data, 10) == [4, 7]


def test_validation_reports_owner_key_on_non_jarldom():
    world_data = make_world()
    world_data["jarldom_owners"] = {"3": "10", "8": "10"}

    assert "owner_key_not_jarldom" in issue_codes(world_data)


def test_validation_reports_unknown_owner_jarldom():
    world_data = make_world()
    world_data["jarldom_owners"] = {"999": "10"}

    assert "unknown_owner_jarldom" in issue_codes(world_data)


def test_validation_reports_unknown_owner_character():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "999"}

    assert "unknown_owner_character" in issue_codes(world_data)


def test_validation_uses_only_global_character_registry():
    world_data = make_world()
    world_data["nodes"]["4"]["characters"] = [{"id": 99}]
    world_data["jarldom_owners"] = {"4": "99"}

    assert "unknown_owner_character" in issue_codes(world_data)


def test_validation_reports_jarldom_without_owner_in_strict_mode():
    world_data = make_world()

    assert "jarldom_missing_owner" not in issue_codes(world_data)
    assert "jarldom_missing_owner" in issue_codes(world_data, strict=True)


def test_relation_adapter_ignores_personal_province_owner_fields():
    world_data = make_world()
    world_data["nodes"]["4"].update(
        {"owner_assigned_id": 10, "owner_assigned_level": "jarldom"}
    )

    assert get_title_seat(world_data, 3) is None
    assert get_jarldom_owner(world_data, 4) is None


def test_relation_adapter_does_not_infer_owner_from_ruler_id():
    world_data = make_world()
    world_data["nodes"]["4"]["ruler_id"] = 10

    assert get_jarldom_owner(world_data, 4) is None


def test_relation_adapter_does_not_infer_seat_from_personal_province_path():
    world_data = make_world()
    world_data["nodes"]["2"]["personal_province_path"] = [2, 3, 4]

    assert get_title_seat(world_data, 2) is None


def test_validation_handles_parent_cycle_without_crashing():
    world_data = make_world()
    world_data["nodes"]["2"]["parent_id"] = 3
    world_data["title_seats"] = {"2": "4"}

    assert "seat_source_not_title" in issue_codes(world_data)


def test_invalid_ids_do_not_crash_queries_or_validation():
    world_data = make_world()
    world_data["title_seats"] = {"bad": "", None: []}
    world_data["jarldom_owners"] = {"bad": {}, "4": "not-a-character"}

    assert get_title_seat(world_data, "") is None
    assert get_seated_title(world_data, object()) is None
    assert get_jarldom_owner(world_data, True) is None
    assert get_owned_jarldoms(world_data, "invalid") == []
    assert {
        "unknown_title_node",
        "unknown_seat_node",
        "unknown_owner_jarldom",
        "unknown_owner_character",
    }.issubset(issue_codes(world_data))


def test_non_mapping_world_data_is_treated_as_empty():
    assert get_title_seat(None, 1) is None
    assert validate_world_relations([]) == []


def test_validation_accepts_node_id_when_node_key_is_invalid():
    world_data = {
        "nodes": {
            "invalid-key": {"node_id": 1, "parent_id": None},
            "2": {"node_id": 2, "parent_id": 999},
        },
        "title_seats": {"1": "2"},
    }

    assert "seat_not_jarldom" in issue_codes(world_data)


def test_relation_issue_is_frozen_and_machine_readable():
    issue = RelationIssue("example", 1, 2, "message")

    assert issue.code == "example"
    assert issue.source_id == 1
    assert issue.target_id == 2
    assert issue.message == "message"


def assert_rejected_without_mutation(function, world_data, *args):
    original = copy.deepcopy(world_data)

    issues = function(world_data, *args)

    assert issues
    assert world_data == original
    return {issue.code for issue in issues}


def test_set_title_seat_creates_index_on_success():
    world_data = make_world()

    set_title_seat(world_data, "2", 4)

    assert world_data["title_seats"] == {"2": "4"}


def test_set_title_seat_returns_no_issues_on_success():
    assert set_title_seat(make_world(), 2, 4) == []


def test_set_title_seat_is_idempotent_for_same_relation():
    world_data = make_world()
    set_title_seat(world_data, 2, 4)
    original = copy.deepcopy(world_data)

    assert set_title_seat(world_data, "2", "4") == []
    assert world_data == original


def test_set_title_seat_can_replace_same_titles_seat():
    world_data = make_world()
    world_data["nodes"]["9"] = {"node_id": 9, "parent_id": 3}
    world_data["title_seats"] = {"2": "4"}

    assert set_title_seat(world_data, 2, 9) == []
    assert world_data["title_seats"] == {"2": "9"}


def test_set_title_seat_rejects_unknown_title_without_mutation():
    codes = assert_rejected_without_mutation(set_title_seat, make_world(), 999, 4)
    assert "unknown_title_node" in codes


def test_set_title_seat_rejects_non_title_source_without_mutation():
    codes = assert_rejected_without_mutation(set_title_seat, make_world(), 4, 4)
    assert "seat_source_not_title" in codes


def test_set_title_seat_rejects_unknown_seat_without_mutation():
    codes = assert_rejected_without_mutation(set_title_seat, make_world(), 2, 999)
    assert "unknown_seat_node" in codes


def test_set_title_seat_rejects_non_jarldom_seat_without_mutation():
    codes = assert_rejected_without_mutation(set_title_seat, make_world(), 2, 3)
    assert "seat_not_jarldom" in codes


def test_set_title_seat_rejects_seat_outside_subtree_without_mutation():
    codes = assert_rejected_without_mutation(set_title_seat, make_world(), 2, 7)
    assert "seat_outside_title_subtree" in codes


def test_set_title_seat_rejects_duplicate_seat_for_other_title_without_mutation():
    world_data = make_world()
    world_data["title_seats"] = {"1": "4"}

    codes = assert_rejected_without_mutation(set_title_seat, world_data, 2, 4)

    assert "duplicate_title_seat" in codes


def test_set_title_seat_rejects_invalid_ids_without_mutation():
    world_data = make_world()
    codes = assert_rejected_without_mutation(set_title_seat, world_data, "bad", [])
    assert {"invalid_title_id", "invalid_seat_id"}.issubset(codes)
    assert "title_seats" not in world_data


def test_set_title_seat_does_not_touch_personal_province_fields():
    world_data = make_world()
    world_data["nodes"]["2"].update(
        {
            "owner_assigned_id": 10,
            "owner_assigned_level": 2,
            "personal_province_path": [2, 3, 4],
        }
    )
    node_before = copy.deepcopy(world_data["nodes"]["2"])

    set_title_seat(world_data, 2, 4)

    assert world_data["nodes"]["2"] == node_before


def test_set_title_seat_does_not_touch_ruler_fields():
    world_data = make_world()
    world_data["nodes"]["2"]["ruler_id"] = 10
    world_data["characters"]["10"]["ruler_of"] = [2]
    original_nodes = copy.deepcopy(world_data["nodes"])
    original_characters = copy.deepcopy(world_data["characters"])

    set_title_seat(world_data, 2, 4)

    assert world_data["nodes"] == original_nodes
    assert world_data["characters"] == original_characters


def test_clear_title_seat_removes_only_that_title_relation():
    world_data = make_world()
    world_data["title_seats"] = {"1": "7", "2": "4"}

    assert clear_title_seat(world_data, 2) == []
    assert world_data["title_seats"] == {"1": "7"}


def test_clear_title_seat_noops_when_index_missing():
    world_data = make_world()
    original = copy.deepcopy(world_data)

    assert clear_title_seat(world_data, 2) == []
    assert world_data == original


def test_clear_title_seat_noops_when_title_has_no_seat():
    world_data = make_world()
    world_data["title_seats"] = {"1": "7"}
    original = copy.deepcopy(world_data)

    assert clear_title_seat(world_data, 2) == []
    assert world_data == original


def test_clear_title_seat_rejects_unknown_title_without_mutation():
    codes = assert_rejected_without_mutation(clear_title_seat, make_world(), 999)
    assert "unknown_title_node" in codes


def test_clear_title_seat_rejects_non_title_without_mutation():
    codes = assert_rejected_without_mutation(clear_title_seat, make_world(), 4)
    assert "seat_source_not_title" in codes


def test_clear_title_seat_rejects_invalid_id_without_mutation():
    codes = assert_rejected_without_mutation(clear_title_seat, make_world(), True)
    assert "invalid_title_id" in codes


def test_set_jarldom_owner_creates_index_on_success():
    world_data = make_world()

    set_jarldom_owner(world_data, "4", 10)

    assert world_data["jarldom_owners"] == {"4": "10"}


def test_set_jarldom_owner_returns_no_issues_on_success():
    assert set_jarldom_owner(make_world(), 4, 10) == []


def test_set_jarldom_owner_is_idempotent_for_same_relation():
    world_data = make_world()
    set_jarldom_owner(world_data, 4, 10)
    original = copy.deepcopy(world_data)

    assert set_jarldom_owner(world_data, "4", "10") == []
    assert world_data == original


def test_set_jarldom_owner_can_replace_owner():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "10"}

    assert set_jarldom_owner(world_data, 4, 11) == []
    assert world_data["jarldom_owners"] == {"4": "11"}


def test_set_jarldom_owner_allows_same_character_to_own_multiple_jarldoms():
    world_data = make_world()

    assert set_jarldom_owner(world_data, 4, 10) == []
    assert set_jarldom_owner(world_data, 7, 10) == []
    assert world_data["jarldom_owners"] == {"4": "10", "7": "10"}


def test_set_jarldom_owner_rejects_unknown_jarldom_without_mutation():
    codes = assert_rejected_without_mutation(set_jarldom_owner, make_world(), 999, 10)
    assert "unknown_owner_jarldom" in codes


def test_set_jarldom_owner_rejects_non_jarldom_key_without_mutation():
    codes = assert_rejected_without_mutation(set_jarldom_owner, make_world(), 3, 10)
    assert "owner_key_not_jarldom" in codes


def test_set_jarldom_owner_rejects_unknown_character_without_mutation():
    codes = assert_rejected_without_mutation(set_jarldom_owner, make_world(), 4, 999)
    assert "unknown_owner_character" in codes


def test_set_jarldom_owner_rejects_invalid_ids_without_mutation():
    world_data = make_world()
    codes = assert_rejected_without_mutation(
        set_jarldom_owner, world_data, object(), False
    )
    assert {"invalid_jarldom_id", "invalid_character_id"}.issubset(codes)
    assert "jarldom_owners" not in world_data


def test_set_jarldom_owner_does_not_infer_or_touch_ruler_id():
    world_data = make_world()
    world_data["nodes"]["4"]["ruler_id"] = 11
    original_nodes = copy.deepcopy(world_data["nodes"])

    assert set_jarldom_owner(world_data, 4, 10) == []
    assert world_data["jarldom_owners"] == {"4": "10"}
    assert world_data["nodes"] == original_nodes


def test_set_jarldom_owner_does_not_touch_owner_assigned_fields():
    world_data = make_world()
    world_data["nodes"]["4"].update(
        {"owner_assigned_id": 11, "owner_assigned_level": 3}
    )
    original_nodes = copy.deepcopy(world_data["nodes"])

    set_jarldom_owner(world_data, 4, 10)

    assert world_data["nodes"] == original_nodes


def test_clear_jarldom_owner_removes_only_that_jarldom_relation():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "10", "7": "11"}

    assert clear_jarldom_owner(world_data, 4) == []
    assert world_data["jarldom_owners"] == {"7": "11"}


def test_clear_jarldom_owner_noops_when_index_missing():
    world_data = make_world()
    original = copy.deepcopy(world_data)

    assert clear_jarldom_owner(world_data, 4) == []
    assert world_data == original


def test_clear_jarldom_owner_noops_when_jarldom_has_no_owner():
    world_data = make_world()
    world_data["jarldom_owners"] = {"7": "11"}
    original = copy.deepcopy(world_data)

    assert clear_jarldom_owner(world_data, 4) == []
    assert world_data == original


def test_clear_jarldom_owner_rejects_unknown_jarldom_without_mutation():
    codes = assert_rejected_without_mutation(clear_jarldom_owner, make_world(), 999)
    assert "unknown_owner_jarldom" in codes


def test_clear_jarldom_owner_rejects_non_jarldom_without_mutation():
    codes = assert_rejected_without_mutation(clear_jarldom_owner, make_world(), 3)
    assert "owner_key_not_jarldom" in codes


def test_clear_jarldom_owner_rejects_invalid_id_without_mutation():
    codes = assert_rejected_without_mutation(
        clear_jarldom_owner, make_world(), "not-an-id"
    )
    assert "invalid_jarldom_id" in codes


def test_read_queries_see_values_written_by_setters():
    world_data = make_world()

    set_title_seat(world_data, 2, 4)
    set_jarldom_owner(world_data, 4, 10)
    set_jarldom_owner(world_data, 7, 10)

    assert get_title_seat(world_data, 2) == 4
    assert get_seated_title(world_data, 4) == 2
    assert get_jarldom_owner(world_data, 4) == 10
    assert get_owned_jarldoms(world_data, 10) == [4, 7]


def test_validate_world_relations_accepts_values_written_by_setters():
    world_data = make_world()

    set_title_seat(world_data, 2, 4)
    set_jarldom_owner(world_data, 4, 10)

    assert validate_world_relations(world_data) == []


def test_failed_title_seat_update_leaves_world_data_exactly_unchanged():
    world_data = make_world()
    world_data["title_seats"] = {"2": "4"}
    original = copy.deepcopy(world_data)

    assert set_title_seat(world_data, 2, 7)
    assert world_data == original


def test_failed_jarldom_owner_update_leaves_world_data_exactly_unchanged():
    world_data = make_world()
    world_data["jarldom_owners"] = {"4": "10"}
    original = copy.deepcopy(world_data)

    assert set_jarldom_owner(world_data, 4, 999)
    assert world_data == original
