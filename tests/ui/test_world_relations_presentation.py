"""Headless tests for world relation presentation helpers."""

from copy import deepcopy

import pytest

from src import world_relations
from src.ui import world_relations_presentation as presentation


def world_data():
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {"node_id": 2, "parent_id": 1},
            "3": {"node_id": 3, "parent_id": 2},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "ruler_id": None,
                "owner_assigned_id": None,
            },
            "5": {"node_id": 5, "parent_id": 3},
        },
        "characters": {"7": {"name": "Alva"}, "8": {"name": "Bo"}},
    }


def rows_by_key(result):
    return {row["key"]: row for row in result["rows"]}


def test_title_relation_presentation_uses_get_title_seat(monkeypatch):
    data = world_data()
    monkeypatch.setattr(presentation.world_relations, "get_title_seat", lambda *_: 4)
    result = presentation.build_title_relations_presentation(
        data, 1, get_node_label=lambda node_id: "Björkdalen"
    )
    assert rows_by_key(result)["title_seat"] == {
        "key": "title_seat",
        "label": "Titelns säte",
        "value": "Björkdalen (ID 4)",
        "target_id": 4,
        "status": "ok",
    }


def test_title_relation_presentation_shows_missing_seat_text():
    row = rows_by_key(presentation.build_title_relations_presentation(world_data(), 1))[
        "title_seat"
    ]
    assert row["value"] == "Inget säte angivet"
    assert row["status"] == "missing"


def test_title_relation_presentation_does_not_use_personal_province_path():
    data = world_data()
    data["nodes"]["1"]["personal_province_path"] = [1, 2, 3, 4]
    result = presentation.build_title_relations_presentation(data, 1)
    assert rows_by_key(result)["title_seat"]["value"] == "Inget säte angivet"


def test_title_relation_presentation_uses_node_label_callback():
    data = world_data()
    data["title_seats"] = {"1": "4"}
    result = presentation.build_title_relations_presentation(
        data, 1, get_node_label=lambda node_id: f"Säte {node_id}"
    )
    assert rows_by_key(result)["title_seat"]["value"] == "Säte 4 (ID 4)"


def test_title_relation_presentation_falls_back_without_node_label_callback():
    data = world_data()
    data["title_seats"] = {"1": "4"}
    result = presentation.build_title_relations_presentation(data, 1)
    assert rows_by_key(result)["title_seat"]["value"] == "Nod 4 (ID 4)"


def test_jarldom_relation_presentation_shows_explicit_owner():
    data = world_data()
    data["jarldom_owners"] = {"4": "7"}
    result = presentation.build_jarldom_relations_presentation(data, 4)
    row = rows_by_key(result)["jarldom_owner"]
    assert row["label"] == "Jarldömets ägare"
    assert row["target_id"] == 7


def test_jarldom_relation_presentation_shows_missing_owner_text():
    result = presentation.build_jarldom_relations_presentation(world_data(), 4)
    assert rows_by_key(result)["jarldom_owner"]["value"] == "Ingen ägare angiven"


def test_jarldom_relation_presentation_does_not_fallback_to_ruler():
    data = world_data()
    data["nodes"]["4"]["ruler_id"] = 8
    result = presentation.build_jarldom_relations_presentation(data, 4)
    rows = rows_by_key(result)
    assert rows["jarldom_owner"]["value"] == "Ingen ägare angiven"
    assert rows["ruler"]["value"] == "Karaktär 8 (ID 8)"


def test_jarldom_relation_presentation_keeps_owner_and_ruler_separate():
    data = world_data()
    data["jarldom_owners"] = {"4": "7"}
    data["nodes"]["4"]["ruler_id"] = 8
    rows = rows_by_key(presentation.build_jarldom_relations_presentation(data, 4))
    assert rows["jarldom_owner"]["target_id"] == 7
    assert rows["ruler"]["target_id"] == 8


def test_jarldom_relation_presentation_keeps_personal_anchor_separate():
    data = world_data()
    data["nodes"]["4"]["owner_assigned_id"] = 2
    rows = rows_by_key(presentation.build_jarldom_relations_presentation(data, 4))
    assert rows["personal_province_anchor"]["target_id"] == 2
    assert rows["jarldom_owner"]["target_id"] is None


def test_jarldom_relation_presentation_shows_seat_for_title():
    data = world_data()
    data["title_seats"] = {"1": "4"}
    result = presentation.build_jarldom_relations_presentation(
        data, 4, get_node_label=lambda node_id: "Nordriket"
    )
    assert rows_by_key(result)["seat_for_title"]["value"] == ("Nordriket (ID 1)")


def test_jarldom_relation_presentation_shows_not_seat_text():
    result = presentation.build_jarldom_relations_presentation(world_data(), 4)
    assert rows_by_key(result)["seat_for_title"]["value"] == (
        "Inte säte för någon titel"
    )


def test_jarldom_relation_presentation_uses_global_character_registry():
    data = world_data()
    data["characters"] = {}
    data["nodes"]["4"]["characters"] = [{"id": 7, "name": "Lokal person"}]
    data["jarldom_owners"] = {"4": "7"}
    result = presentation.build_jarldom_relations_presentation(data, 4)
    assert "Lokal person" not in rows_by_key(result)["jarldom_owner"]["value"]
    assert result["warnings"][0]["code"] == "unknown_owner_character"


def test_jarldom_relation_presentation_uses_character_label_callback():
    data = world_data()
    data["jarldom_owners"] = {"4": "7"}
    result = presentation.build_jarldom_relations_presentation(
        data, 4, get_character_label=lambda character_id: "Alva Silverhand"
    )
    assert rows_by_key(result)["jarldom_owner"]["value"] == ("Alva Silverhand (ID 7)")


def test_jarldom_relation_presentation_falls_back_without_character_callback():
    data = world_data()
    data["jarldom_owners"] = {"4": "7"}
    result = presentation.build_jarldom_relations_presentation(data, 4)
    assert rows_by_key(result)["jarldom_owner"]["value"] == ("Karaktär 7 (ID 7)")


@pytest.mark.parametrize(
    ("builder", "node_id", "code", "expected"),
    (
        (
            presentation.build_title_relations_presentation,
            1,
            "title_missing_seat",
            "Titeln saknar angivet säte.",
        ),
        (
            presentation.build_jarldom_relations_presentation,
            4,
            "jarldom_missing_owner",
            "Jarldömet saknar angiven ägare.",
        ),
        (
            presentation.build_title_relations_presentation,
            1,
            "duplicate_title_seat",
            "Jarldömet används redan som säte för en annan titel.",
        ),
        (
            presentation.build_title_relations_presentation,
            1,
            "seat_outside_title_subtree",
            "Sätet ligger utanför titelns område.",
        ),
        (
            presentation.build_jarldom_relations_presentation,
            4,
            "unknown_owner_character",
            "Den angivna ägarkaraktären finns inte längre.",
        ),
    ),
)
def test_relation_presentation_maps_warnings(
    monkeypatch, builder, node_id, code, expected
):
    issue = world_relations.RelationIssue(code, node_id, None)
    monkeypatch.setattr(
        presentation.world_relations,
        "validate_world_relations",
        lambda *_args, **_kw: [issue],
    )
    assert builder(world_data(), node_id)["warnings"][0]["label"] == expected


def test_relation_presentation_maps_unknown_issue_code_to_neutral_warning(
    monkeypatch,
):
    issue = world_relations.RelationIssue("future_issue", 1, None)
    monkeypatch.setattr(
        presentation.world_relations,
        "validate_world_relations",
        lambda *_args, **_kw: [issue],
    )
    result = presentation.build_title_relations_presentation(world_data(), 1)
    assert result["warnings"][0]["label"] == "Okänt relationsproblem."


def test_relation_presentation_does_not_mutate_world_data():
    data = world_data()
    expected = deepcopy(data)
    presentation.build_title_relations_presentation(data, 1)
    presentation.build_jarldom_relations_presentation(data, 4)
    assert data == expected


def test_relation_presentation_does_not_create_relation_indexes():
    data = world_data()
    presentation.build_title_relations_presentation(data, 1)
    presentation.build_jarldom_relations_presentation(data, 4)
    assert "title_seats" not in data
    assert "jarldom_owners" not in data


def test_relation_presentation_does_not_call_setters(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("A relation setter was called")

    monkeypatch.setattr(presentation.world_relations, "set_title_seat", fail)
    monkeypatch.setattr(presentation.world_relations, "clear_title_seat", fail)
    monkeypatch.setattr(presentation.world_relations, "set_jarldom_owner", fail)
    monkeypatch.setattr(presentation.world_relations, "clear_jarldom_owner", fail)
    presentation.build_title_relations_presentation(world_data(), 1)
    presentation.build_jarldom_relations_presentation(world_data(), 4)


def test_relation_presentation_uses_required_swedish_labels():
    title_result = presentation.build_title_relations_presentation(world_data(), 1)
    jarldom_result = presentation.build_jarldom_relations_presentation(world_data(), 4)
    labels = {
        row["label"]
        for result in (title_result, jarldom_result)
        for row in result["rows"]
    }
    assert labels == {
        "Jarldömets ägare",
        "Titelns säte",
        "Säte för titel",
        "Personlig provins / titelankare",
        "Härskare",
    }


def test_relation_presentation_does_not_use_ambiguous_owner_labels():
    result = presentation.build_jarldom_relations_presentation(world_data(), 4)
    labels = {row["label"] for row in result["rows"]}
    assert labels.isdisjoint({"Ägare", "Ägande", "Ägarnoder", "Lokal ägo"})


def test_relation_presentation_does_not_duplicate_callback_id():
    data = world_data()
    data["title_seats"] = {"1": "4"}
    result = presentation.build_title_relations_presentation(
        data, 1, get_node_label=lambda node_id: "Björkdalen (ID 4)"
    )
    assert rows_by_key(result)["title_seat"]["value"] == "Björkdalen (ID 4)"
