"""Tests for the reported physical storage presentation helper."""

import inspect

import pytest

from src.ui.storage_presentation import build_reported_storage_overview

KEYS = (
    "storage_basic",
    "storage_luxury",
    "storage_silver",
    "storage_timber",
    "storage_coal",
    "storage_iron_ore",
    "storage_iron",
    "storage_animal_feed",
    "storage_skin",
)
LABELS = (
    "Basresurser (BAS)",
    "Lyxresurser (LYX)",
    "Silver",
    "Timmer",
    "Kol",
    "Järnmalm",
    "Järn",
    "Djurfoder",
    "Skinn",
)


class StubWorldManager:
    def __init__(self, report):
        self.report = report
        self.reported_node_ids = []

    def get_storage_report(self, node_id):
        self.reported_node_ids.append(node_id)
        return self.report


def build_overview(report=None, node_id=42):
    manager = StubWorldManager(report if report is not None else {})
    return build_reported_storage_overview(manager, node_id), manager


def test_reported_storage_overview_uses_world_manager_report():
    overview, _ = build_overview({"storage_basic": 7})
    assert overview["rows"][0]["value"] == 7


def test_reported_storage_overview_calls_report_with_node_id():
    _, manager = build_overview(node_id="jarldom-1")
    assert manager.reported_node_ids == ["jarldom-1"]


def test_reported_storage_overview_returns_expected_title():
    overview, _ = build_overview()
    assert overview["title"] == "Rapporterat fysiskt lager"


def test_reported_storage_overview_returns_required_help_text():
    overview, _ = build_overview()
    assert overview["help_text"] == (
        "Summerat från Lager-noder i området; inte automatiskt disponibelt."
    )


def test_reported_storage_overview_returns_all_nine_rows_in_policy_order():
    overview, _ = build_overview()
    assert tuple(row["key"] for row in overview["rows"]) == KEYS
    assert tuple(row["label"] for row in overview["rows"]) == LABELS


def test_reported_storage_overview_uses_consistent_swedish_labels():
    overview, _ = build_overview()
    labels = {row["key"]: row["label"] for row in overview["rows"]}
    assert labels["storage_basic"] == "Basresurser (BAS)"
    assert labels["storage_luxury"] == "Lyxresurser (LYX)"
    assert labels["storage_silver"] == "Silver"


def test_reported_storage_overview_preserves_zero_values():
    overview, _ = build_overview(dict.fromkeys(KEYS, 0))
    assert all(row["value"] == 0 for row in overview["rows"])
    assert all(type(row["value"]) is int for row in overview["rows"])


def test_reported_storage_overview_does_not_use_missing_text():
    overview, _ = build_overview()
    assert "Saknas ännu" not in repr(overview)


def test_reported_storage_overview_does_not_mix_node_legacy_fields():
    parameters = inspect.signature(build_reported_storage_overview).parameters
    assert tuple(parameters) == ("world_manager", "node_id")
    with pytest.raises(TypeError):
        build_reported_storage_overview(
            StubWorldManager({"storage_basic": 7}),
            42,
            node_data={"storage_basic": 100},
        )


def test_reported_storage_overview_marks_report_as_not_automatically_available():
    overview, _ = build_overview()
    assert "inte automatiskt disponibelt" in overview["help_text"]


def test_reported_storage_overview_does_not_claim_ownership_or_tax():
    overview, _ = build_overview()
    forbidden = ("ägt", "skattebart", "konsumtion", "förbrukning", "tillgängligt")
    assert not any(word in overview["help_text"] for word in forbidden)


def test_reported_storage_overview_does_not_mutate_report():
    report = {"storage_basic": 7, "metadata": {"source": "report"}}
    expected = {"storage_basic": 7, "metadata": {"source": "report"}}
    build_overview(report)
    assert report == expected


def test_reported_storage_overview_handles_missing_keys_as_zero():
    overview, _ = build_overview({"storage_basic": 7})
    assert [row["value"] for row in overview["rows"]] == [7] + [0] * 8


def test_reported_storage_overview_values_are_integers():
    overview, _ = build_overview({key: index for index, key in enumerate(KEYS)})
    assert all(isinstance(row["value"], int) for row in overview["rows"])
