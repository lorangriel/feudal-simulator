from src.ui_strings import (
    DETAILS_PLACEHOLDER,
    PANEL_NAMES,
    format_details_title,
    format_panel_name,
)


def test_panel_names_are_consistent():
    assert PANEL_NAMES["structure"] == "Struktur"
    assert PANEL_NAMES["status"] == "Status"
    assert PANEL_NAMES["details"] == "Detaljer"


def test_format_details_title_with_and_without_resource():
    assert format_details_title("Kungarike") == "Detaljer: Kungarike"
    assert format_details_title(None) == f"Detaljer: {DETAILS_PLACEHOLDER}"


def test_format_panel_name_pass_through_unknown():
    assert format_panel_name("structure") == "Struktur"
    assert format_panel_name("okänd") == "okänd"
