"""Centralised UI text used across the Tk-gränssnittet.

This module keeps the visible panelnamn samlade så att etiketter,
loggar och tester alltid använder samma strängar.
"""

from __future__ import annotations

PANEL_NAMES = {
    "structure": "Struktur",
    "status": "Status",
    "details": "Detaljer",
}

DETAILS_PLACEHOLDER = "Ingen vald enhet"


def format_panel_name(panel_key: str) -> str:
    """Return the configured panel name for ``panel_key``."""

    return PANEL_NAMES.get(panel_key, panel_key)


def format_details_title(resource_name: str | None) -> str:
    """Return the Detaljer-rubrik med resursens namn.

    Ensures the heading always follows the ``Detaljer: <resurs>`` format,
    even when no resource is aktiv.
    """

    display_name = (resource_name or "").strip() or DETAILS_PLACEHOLDER
    return f"{PANEL_NAMES['details']}: {display_name}"


def panel_tooltip(panel_key: str) -> str:
    """Return a short tooltip describing the given panel."""

    descriptions = {
        "structure": "Hierarkipanelen för noder och resurser.",
        "status": "Senaste statusmeddelanden för arbetet.",
        "details": "Aktiv redigeringspanel för vald enhet.",
    }
    base = format_panel_name(panel_key)
    return f"{base} – {descriptions.get(panel_key, 'Panel')}"
