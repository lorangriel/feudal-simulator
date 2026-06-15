import copy
import inspect
import tkinter as tk
from tkinter import ttk

import pytest

from src.ui import app as ui_app
from ui.views import node_details_view
from ui.views.node_details_view import NodeDetailsView


@pytest.fixture
def root():
    try:
        tk_root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    tk_root.withdraw()
    yield tk_root
    tk_root.destroy()


def _build_world():
    return {
        "nodes": {
            str(node_id): {
                "node_id": node_id,
                "parent_id": node_id - 1 if node_id > 1 else None,
                "children": [node_id + 1] if node_id < 5 else [],
            }
            for node_id in range(1, 6)
        }
    }


@pytest.mark.parametrize(
    ("depth", "expected_tab"),
    [
        (0, "Vasaller & bidrag"),
        (1, "Vasaller & bidrag"),
        (2, "Vasaller & bidrag"),
        (3, "Domänöversikt"),
        (4, "Förvaltning"),
        (7, "Förvaltning"),
    ],
)
def test_notebook_tab_label_for_depth(depth, expected_tab):
    assert NodeDetailsView._notebook_tab_for_depth(depth) == expected_tab


def _find_notebook(widget):
    for child in widget.winfo_children():
        if isinstance(child, ttk.Notebook):
            return child
        notebook = _find_notebook(child)
        if notebook is not None:
            return notebook
    return None


def _is_descendant(widget, ancestor):
    current = widget
    while current is not None:
        if current is ancestor:
            return True
        current = current.master
    return False


def _descendant_texts(widget):
    texts = []
    for child in widget.winfo_children():
        if isinstance(child, (ttk.Label, ttk.LabelFrame)):
            texts.append(child.cget("text"))
        texts.extend(_descendant_texts(child))
    return texts


def _descendants_of_type(widget, widget_types):
    matches = []
    for child in widget.winfo_children():
        if isinstance(child, widget_types):
            matches.append(child)
        matches.extend(_descendants_of_type(child, widget_types))
    return matches


def _show_domain_overview(app, monkeypatch):
    monkeypatch.setattr(app, "_show_jarldome_editor", lambda parent, node: None)
    app.show_node_view(app.world_data["nodes"]["4"])
    notebook = _find_notebook(app.details_panel.body)
    return notebook.nametowidget(notebook.tabs()[1])


def _show_management_overview(app, monkeypatch):
    monkeypatch.setattr(app, "_show_resource_editor", lambda parent, node, depth: None)
    app.show_node_view(app.world_data["nodes"]["5"])
    notebook = _find_notebook(app.details_panel.body)
    return notebook.nametowidget(notebook.tabs()[1])


def _show_vassals_overview(app, monkeypatch, node_id=1):
    monkeypatch.setattr(
        app, "_show_upper_level_node_editor", lambda parent, node, depth: None
    )
    app.show_node_view(app.world_data["nodes"][str(node_id)])
    notebook = _find_notebook(app.details_panel.body)
    return notebook.nametowidget(notebook.tabs()[1])


def _find_reported_storage_section(presentation_frame):
    return next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Rapporterat fysiskt lager"
    )


@pytest.mark.parametrize(
    ("node_id", "expected_tab", "expected_editor"),
    [
        (1, "Vasaller & bidrag", "upper"),
        (2, "Vasaller & bidrag", "upper"),
        (3, "Vasaller & bidrag", "upper"),
        (4, "Domänöversikt", "jarldome"),
        (5, "Förvaltning", "resource"),
    ],
)
def test_node_depth_uses_editing_and_presentation_tabs_and_calls_editor_once(
    root, monkeypatch, node_id, expected_tab, expected_editor
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    editor_calls = []

    monkeypatch.setattr(
        app,
        "_show_upper_level_node_editor",
        lambda parent, node, depth: editor_calls.append(("upper", parent)),
    )
    monkeypatch.setattr(
        app,
        "_show_jarldome_editor",
        lambda parent, node: editor_calls.append(("jarldome", parent)),
    )
    monkeypatch.setattr(
        app,
        "_show_resource_editor",
        lambda parent, node, depth: editor_calls.append(("resource", parent)),
    )

    app.show_node_view(app.world_data["nodes"][str(node_id)])

    notebook = _find_notebook(app.details_panel.body)
    assert notebook is not None
    assert [notebook.tab(tab_id, "text") for tab_id in notebook.tabs()] == [
        "Redigering",
        expected_tab,
    ]
    assert [editor for editor, _parent in editor_calls] == [expected_editor]
    tab_frame = notebook.nametowidget(notebook.tabs()[0])
    assert _is_descendant(editor_calls[0][1], tab_frame)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    assert not _is_descendant(editor_calls[0][1], presentation_frame)


def test_domain_overview_contains_read_only_sections(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    texts = _descendant_texts(presentation_frame)
    assert {
        "Sammanfattning",
        "Undernoder",
        "Arbete/DV",
        "Rapporterat fysiskt lager",
        "Soldater",
        "Umbärande",
    }.issubset(texts)
    assert not _descendants_of_type(
        presentation_frame, (ttk.Entry, ttk.Combobox, ttk.Spinbox)
    )


def test_domain_overview_shows_reported_physical_storage_section(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_domain_overview(app, monkeypatch))

    assert "Rapporterat fysiskt lager" in texts


def test_domain_overview_does_not_show_bare_lager_section_for_report(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    section_titles = [
        section.cget("text")
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
    ]

    assert "Lager" not in section_titles


def test_domain_overview_shows_storage_help_text(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_domain_overview(app, monkeypatch))

    assert "Summerat från Lager-noder i området; inte automatiskt disponibelt." in texts


def test_domain_overview_shows_all_reported_storage_rows(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_domain_overview(app, monkeypatch))

    expected_labels = {
        "Basresurser (BAS):",
        "Lyxresurser (LYX):",
        "Silver:",
        "Timmer:",
        "Kol:",
        "Järnmalm:",
        "Järn:",
        "Djurfoder:",
        "Skinn:",
    }
    assert expected_labels.issubset(texts)


def test_domain_overview_shows_zero_storage_values_as_zero(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Rapporterat fysiskt lager"
    )
    texts = _descendant_texts(storage_section)

    assert texts.count("0") == 9
    assert "Saknas ännu" not in texts


def test_domain_overview_uses_reported_storage_overview_helper(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    calls = []

    def build_overview(world_manager, node_id):
        calls.append((world_manager, node_id))
        return {
            "title": "Rapporterat fysiskt lager",
            "help_text": (
                "Summerat från Lager-noder i området; " "inte automatiskt disponibelt."
            ),
            "rows": ({"label": "Hjälpervärde", "value": 73},),
        }

    monkeypatch.setattr(
        node_details_view,
        "build_reported_storage_overview",
        build_overview,
    )

    texts = _descendant_texts(_show_domain_overview(app, monkeypatch))

    assert calls == [(app.world_manager, 4)]
    assert {"Hjälpervärde:", "73"}.issubset(texts)


def test_domain_overview_does_not_mix_jarldom_legacy_storage_into_report(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["4"]["storage_basic"] = 100
    app.world_data["nodes"]["5"].update({"res_type": "Lager", "storage_basic": 7})
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Rapporterat fysiskt lager"
    )
    texts = _descendant_texts(storage_section)

    assert "7" in texts
    assert "100" not in texts
    assert "107" not in texts


def test_domain_overview_storage_report_is_read_only(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Rapporterat fysiskt lager"
    )

    assert not _descendants_of_type(
        storage_section,
        (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox, ttk.Spinbox),
    )


def test_domain_overview_storage_report_does_not_claim_ownership_or_tax(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Rapporterat fysiskt lager"
    )
    storage_text = " ".join(_descendant_texts(storage_section)).lower()

    forbidden = ("ägt", "skattebart", "konsumtion", "förbrukning", "tillgängligt")
    assert not any(word in storage_text for word in forbidden)


def test_domain_overview_handles_missing_optional_values(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(app, "_show_jarldome_editor", lambda parent, node: None)

    app.show_node_view(app.world_data["nodes"]["4"])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    assert "Saknas ännu" in _descendant_texts(presentation_frame)


def test_management_overview_contains_read_only_sections(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(app, "_show_resource_editor", lambda parent, node, depth: None)

    app.show_node_view(app.world_data["nodes"]["5"])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    texts = _descendant_texts(presentation_frame)
    assert {
        "Sammanfattning",
        "Förvaltare",
        "Assistenter",
        "Ansvarsområde",
        "Lokalt lagersaldo",
        "Arbete/DV",
        "Inkomstutmaning",
        "Kostnader",
        "Modifierare",
        "Resultat & logg",
    }.issubset(texts)
    assert not _descendants_of_type(
        presentation_frame,
        (tk.Entry, tk.Text, ttk.Button, ttk.Entry, ttk.Combobox, ttk.Spinbox),
    )


def test_management_overview_uses_existing_values_and_safe_fallbacks(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    node_data = app.world_data["nodes"]["5"]
    node_data.update(
        {
            "res_type": "Lager",
            "population": 12,
            "storage_basic": 34,
            "weather_effect": -2,
        }
    )
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(app, "_show_resource_editor", lambda parent, node, depth: None)

    app.show_node_view(node_data)

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    texts = _descendant_texts(presentation_frame)
    assert {"Lager", "12", "34", "-2"}.issubset(texts)
    assert {
        "Förvaltarmodell är inte implementerad ännu.",
        "Assistenter är inte implementerade ännu.",
        "DV-sammanfattning saknar säker datakälla för denna nod.",
        "Inkomstutmaningar är inte implementerade ännu.",
        "Förvaltningskostnader är inte implementerade ännu.",
        "Resultat- och förvaltningslogg är inte implementerad ännu.",
    }.issubset(texts)


def test_management_overview_lager_node_shows_local_storage_balance(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert "Lokalt lagersaldo" in texts


def test_management_overview_lager_node_shows_local_storage_help_text(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert "Källa: Registrerade värden på denna Lager-nod." in texts


def test_management_overview_lager_node_shows_all_storage_rows(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert {
        "Basresurser (BAS):",
        "Lyxresurser (LYX):",
        "Silver:",
        "Timmer:",
        "Kol:",
        "Järnmalm:",
        "Järn:",
        "Djurfoder:",
        "Skinn:",
    }.issubset(texts)


def test_management_overview_lager_node_shows_zero_values_as_zero(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_management_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Lokalt lagersaldo"
    )
    texts = _descendant_texts(storage_section)

    assert texts.count("0") == 9
    assert "Saknas ännu" not in texts


def test_management_overview_non_lager_node_does_not_show_storage_as_safe_lager(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"].update({"res_type": "Gods", "storage_basic": 100})
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert "Lokalt lagersaldo" not in texts
    assert "100" not in texts


def test_management_overview_non_lager_node_shows_safe_storage_fallback(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Gods"
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert "Ingen säker lagerdatakälla för denna nod." in texts


def test_management_overview_local_storage_is_read_only(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_management_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Lokalt lagersaldo"
    )

    assert not _descendants_of_type(
        storage_section,
        (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox, ttk.Spinbox),
    )


def test_management_overview_does_not_claim_storage_availability_or_tax(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["5"]["res_type"] = "Lager"
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_management_overview(app, monkeypatch)
    storage_section = next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == "Lokalt lagersaldo"
    )
    storage_text = " ".join(_descendant_texts(storage_section)).lower()
    forbidden = (
        "disponibelt",
        "tillgängligt",
        "ägt",
        "skattebart",
        "konsumtion",
        "förbrukning",
    )

    assert not any(word in storage_text for word in forbidden)


def test_management_overview_uses_local_storage_presentation_helper(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    node_data = app.world_data["nodes"]["5"]
    app.world_manager.set_world_data(app.world_data)
    calls = []

    def build_overview(received_node_data):
        calls.append(received_node_data)
        return {
            "title": "Lokalt lagersaldo",
            "help_text": "Källa: Registrerade värden på denna Lager-nod.",
            "rows": ({"label": "Hjälpervärde", "value": 73},),
        }

    monkeypatch.setattr(
        node_details_view,
        "build_local_storage_overview",
        build_overview,
    )

    texts = _descendant_texts(_show_management_overview(app, monkeypatch))

    assert calls == [node_data]
    assert {"Hjälpervärde:", "73"}.issubset(texts)


@pytest.mark.parametrize("node_id", [1, 2, 3, 4])
def test_management_overview_is_not_shown_below_depth_four(root, monkeypatch, node_id):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(
        app, "_show_upper_level_node_editor", lambda parent, node, depth: None
    )
    monkeypatch.setattr(app, "_show_jarldome_editor", lambda parent, node: None)

    app.show_node_view(app.world_data["nodes"][str(node_id)])

    notebook = _find_notebook(app.details_panel.body)
    assert "Förvaltning" not in [
        notebook.tab(tab_id, "text") for tab_id in notebook.tabs()
    ]


@pytest.mark.parametrize("node_id", [1, 2, 3])
def test_vassals_overview_contains_read_only_sections(root, monkeypatch, node_id):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(
        app, "_show_upper_level_node_editor", lambda parent, node, depth: None
    )

    app.show_node_view(app.world_data["nodes"][str(node_id)])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    texts = _descendant_texts(presentation_frame)
    assert {
        "Sammanfattning",
        "Underliggande områden",
        "Rapporterat fysiskt lager",
        "Skatt",
        "Soldater",
        "Status & risk",
        "Flaggor",
        "Åtgärder",
    }.issubset(texts)
    assert not _descendants_of_type(
        presentation_frame, (ttk.Entry, ttk.Combobox, ttk.Spinbox)
    )


def test_vassals_overview_shows_reported_physical_storage_section(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_vassals_overview(app, monkeypatch))

    assert "Rapporterat fysiskt lager" in texts


def test_vassals_overview_shows_storage_help_text(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_vassals_overview(app, monkeypatch))

    assert "Summerat från Lager-noder i området; inte automatiskt disponibelt." in texts


def test_vassals_overview_shows_all_reported_storage_rows(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(_show_vassals_overview(app, monkeypatch))

    assert {
        "Basresurser (BAS):",
        "Lyxresurser (LYX):",
        "Silver:",
        "Timmer:",
        "Kol:",
        "Järnmalm:",
        "Järn:",
        "Djurfoder:",
        "Skinn:",
    }.issubset(texts)


def test_vassals_overview_shows_zero_storage_values_as_zero(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch)
    texts = _descendant_texts(_find_reported_storage_section(presentation_frame))

    assert texts.count("0") == 9
    assert "Saknas ännu" not in texts


def test_vassals_overview_uses_reported_storage_helper(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    calls = []

    def build_overview(world_manager, node_id):
        calls.append((world_manager, node_id))
        return {
            "title": "Rapporterat fysiskt lager",
            "help_text": (
                "Summerat från Lager-noder i området; " "inte automatiskt disponibelt."
            ),
            "rows": ({"label": "Hjälpervärde", "value": 73},),
        }

    monkeypatch.setattr(
        node_details_view,
        "build_reported_storage_overview",
        build_overview,
    )

    texts = _descendant_texts(_show_vassals_overview(app, monkeypatch, node_id=2))

    assert calls == [(app.world_manager, 2)]
    assert {"Hjälpervärde:", "73"}.issubset(texts)


def test_vassals_overview_does_not_mix_upper_node_legacy_storage_into_report(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["nodes"]["1"]["storage_basic"] = 100
    app.world_data["nodes"]["5"].update({"res_type": "Lager", "storage_basic": 7})
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch)
    texts = _descendant_texts(_find_reported_storage_section(presentation_frame))

    assert "7" in texts
    assert "100" not in texts
    assert "107" not in texts


def test_vassals_overview_storage_report_is_read_only(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch)
    storage_section = _find_reported_storage_section(presentation_frame)

    assert not _descendants_of_type(
        storage_section,
        (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox, ttk.Spinbox),
    )


def test_vassals_overview_storage_report_does_not_claim_tax_or_ownership(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch)
    storage_section = _find_reported_storage_section(presentation_frame)
    storage_text = " ".join(_descendant_texts(storage_section)).lower()
    forbidden = (
        "ägt",
        "skattebart",
        "tribut",
        "bidrag",
        "konsumtion",
        "förbrukning",
        "tillgängligt",
    )

    assert not any(word in storage_text for word in forbidden)


def test_vassals_overview_does_not_show_bare_lager_section_for_report(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch)
    section_titles = [
        section.cget("text")
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
    ]

    assert "Lager" not in section_titles


@pytest.mark.parametrize("node_id", [1, 2, 3])
def test_vassals_overview_storage_section_available_on_depths_zero_to_two(
    root, monkeypatch, node_id
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(
        _find_reported_storage_section(
            _show_vassals_overview(app, monkeypatch, node_id=node_id)
        )
    )

    assert "Rapporterat fysiskt lager" not in texts
    assert "Basresurser (BAS):" in texts


def test_vassals_overview_handles_missing_optional_values(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(
        app, "_show_upper_level_node_editor", lambda parent, node, depth: None
    )

    app.show_node_view(app.world_data["nodes"]["1"])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    assert "Saknas ännu" in _descendant_texts(presentation_frame)


def test_level_three_owner_dropdown_remains_outside_notebook(root):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)

    app.show_node_view(app.world_data["nodes"]["4"])

    notebook = _find_notebook(app.details_panel.body)
    assert notebook is not None
    assert app.details_panel.ownership_frame.winfo_manager()
    assert app.details_panel.ownership_frame.master is app.details_panel.body.master
    assert not _is_descendant(app.details_panel.ownership_frame, notebook)
    assert app.details_panel.ownership_combobox.instate(["readonly"])


def _build_relations_world():
    data = _build_world()
    data["characters"] = {
        "10": {"name": "Global ägare"},
        "11": {"name": "Global härskare"},
    }
    data["nodes"]["2"]["children"] = [3, 4]
    data["nodes"]["4"].update(
        {
            "parent_id": 2,
            "children": [5],
            "ruler_id": 11,
            "owner_assigned_level": 2,
            "owner_assigned_id": 2,
            "personal_province_path": [2, 4],
            "characters": [{"id": 10, "name": "Vilseledande lokal ägare"}],
        }
    )
    data["title_seats"] = {"2": 4}
    data["jarldom_owners"] = {"4": 10}
    return data


def _find_section(presentation_frame, title):
    return next(
        section
        for section in _descendants_of_type(presentation_frame, ttk.LabelFrame)
        if section.cget("text") == title
    )


def test_vassals_overview_renders_title_relations_in_existing_tab(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_relations_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_vassals_overview(app, monkeypatch, node_id=2)
    texts = _descendant_texts(_find_section(presentation_frame, "Relationer"))

    assert "Titelns säte:" in texts
    assert any("ID 4" in text for text in texts)
    assert "Vasaller & bidrag" in [
        _find_notebook(app.details_panel.body).tab(tab_id, "text")
        for tab_id in _find_notebook(app.details_panel.body).tabs()
    ]


def test_domain_overview_renders_jarldom_relations_in_existing_tab(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_relations_world()
    app.world_manager.set_world_data(app.world_data)

    presentation_frame = _show_domain_overview(app, monkeypatch)
    texts = _descendant_texts(_find_section(presentation_frame, "Relationer"))

    assert {
        "Jarldömets ägare:",
        "Härskare:",
        "Personlig provins / titelankare:",
        "Säte för titel:",
        "Global ägare (ID 10)",
        "Global härskare (ID 11)",
    }.issubset(texts)
    assert any("ID 2" in text for text in texts)
    assert "Domänöversikt" in [
        _find_notebook(app.details_panel.body).tab(tab_id, "text")
        for tab_id in _find_notebook(app.details_panel.body).tabs()
    ]


def test_relations_use_global_characters_not_ruler_or_anchor_as_owner(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_relations_world()
    app.world_data["characters"]["2"] = {"name": "Fel ankarkaraktär"}
    app.world_data["characters"]["11"] = {"name": "Fel ägare från härskare"}
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(
        _find_section(_show_domain_overview(app, monkeypatch), "Relationer")
    )
    owner_index = texts.index("Jarldömets ägare:") + 1

    assert texts[owner_index] == "Global ägare (ID 10)"
    assert "Vilseledande lokal ägare (ID 10)" not in texts
    assert "Fel ägare från härskare (ID 11)" not in texts[owner_index]
    assert "Fel ankarkaraktär (ID 2)" not in texts[owner_index]


def test_relations_missing_values_and_warnings_render_without_mutation(
    root, monkeypatch
):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_data["characters"] = {}
    before = copy.deepcopy(app.world_data)
    app.world_manager.set_world_data(app.world_data)

    texts = _descendant_texts(
        _find_section(_show_domain_overview(app, monkeypatch), "Relationer")
    )

    assert {
        "Ingen ägare angiven",
        "Ingen härskare angiven",
        "Lokal, inget titelankare",
        "Inte säte för någon titel",
        "Varning:",
        "Jarldömet saknar angiven ägare.",
    }.issubset(texts)
    assert app.world_data == before


def test_relation_rendering_uses_helper_and_does_not_call_setters(monkeypatch):
    calls = []

    def fake_title(world_data, node_id, **kwargs):
        calls.append((world_data, node_id, sorted(kwargs)))
        return {
            "title": "Relationer",
            "rows": ({"label": "Titelns säte", "value": "Hjälparnod"},),
            "warnings": ({"label": "Hjälparvarning"},),
        }

    monkeypatch.setattr(
        node_details_view, "build_title_relations_presentation", fake_title
    )
    monkeypatch.setattr(
        (
            node_details_view.world_relations
            if hasattr(node_details_view, "world_relations")
            else node_details_view
        ),
        "set_title_seat",
        lambda *args, **kwargs: pytest.fail("setter must not be called"),
        raising=False,
    )
    view = object.__new__(NodeDetailsView)
    view.app = type(
        "AppStub",
        (),
        {
            "world_data": {"nodes": {}},
            "get_display_name": lambda self, node_id: f"Nod {node_id}",
        },
    )()

    presentation = view._build_relations_presentation(2, 2)
    rows = NodeDetailsView._relation_rows_for_overview(presentation)

    assert calls == [({"nodes": {}}, 2, ["get_node_label"])]
    assert rows == (("Titelns säte", "Hjälparnod"), ("Varning", "Hjälparvarning"))


def test_level_three_owner_dropdown_label_and_position_remain_unchanged(root):
    app = ui_app.create_app(root)
    app.world_data = _build_relations_world()
    app.world_manager.set_world_data(app.world_data)

    app.show_node_view(app.world_data["nodes"]["4"])

    assert app.details_panel.ownership_label.cget("text") == "Ägande:"
    assert app.details_panel.ownership_combobox.instate(["readonly"])


def test_node_details_view_does_not_call_relation_setters_or_read_maps_directly():
    source = inspect.getsource(node_details_view.NodeDetailsView)

    assert "set_title_seat" not in source
    assert "clear_title_seat" not in source
    assert "set_jarldom_owner" not in source
    assert "clear_jarldom_owner" not in source
    assert 'world_data["title_seats"]' not in source
    assert 'world_data["jarldom_owners"]' not in source
