"""Presentation helpers for reported physical storage."""

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
