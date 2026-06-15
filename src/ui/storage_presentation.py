"""Presentation helpers for physical storage."""

from typing import Any, Mapping

from rollup_policy import STORAGE_RESOURCE_KEYS, get_local_storage_contribution

_STORAGE_ROWS = (
    ("storage_basic", "Basresurser (BAS)"),
    ("storage_luxury", "Lyxresurser (LYX)"),
    ("storage_silver", "Silver"),
    ("storage_timber", "Timmer"),
    ("storage_coal", "Kol"),
    ("storage_iron_ore", "Järnmalm"),
    ("storage_iron", "Järn"),
    ("storage_animal_feed", "Djurfoder"),
    ("storage_skin", "Skinn"),
)

assert tuple(key for key, _label in _STORAGE_ROWS) == STORAGE_RESOURCE_KEYS


def build_local_storage_overview(
    node_data: Mapping[str, Any],
) -> dict | None:
    """Build a presentation model for local storage on a physical Lager node."""
    probe_key = STORAGE_RESOURCE_KEYS[0]
    policy_probe = {**node_data, probe_key: 1}
    if get_local_storage_contribution(policy_probe, probe_key) != 1:
        return None

    contributions = {
        key: get_local_storage_contribution(node_data, key)
        for key in STORAGE_RESOURCE_KEYS
    }

    rows = tuple(
        {"key": key, "label": label, "value": contributions[key]}
        for key, label in _STORAGE_ROWS
    )
    return {
        "title": "Lokalt lagersaldo",
        "help_text": "Källa: Registrerade värden på denna Lager-nod.",
        "rows": rows,
    }


def build_reported_storage_overview(world_manager, node_id) -> dict:
    """Build a presentation model for reported physical storage."""
    report = world_manager.get_storage_report(node_id)
    rows = tuple(
        {"key": key, "label": label, "value": report.get(key, 0)}
        for key, label in _STORAGE_ROWS
    )
    return {
        "title": "Rapporterat fysiskt lager",
        "help_text": (
            "Summerat från Lager-noder i området; " "inte automatiskt disponibelt."
        ),
        "rows": rows,
    }
