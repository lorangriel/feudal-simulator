"""Centralised UI text used across the Tk-gränssnittet.

This module keeps the visible panelnamn samlade så att etiketter,
loggar och tester alltid använder samma strängar.
"""

from __future__ import annotations

from ui.strings import (
    DETAILS_PLACEHOLDER,
    PANEL_NAMES,
    format_details_title,
    format_panel_name,
    panel_tooltip,
)

__all__ = [
    "DETAILS_PLACEHOLDER",
    "PANEL_NAMES",
    "format_details_title",
    "format_panel_name",
    "panel_tooltip",
]
