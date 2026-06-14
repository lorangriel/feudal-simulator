import tkinter as tk
from tkinter import ttk

import pytest

from src.ui import app as ui_app
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

    monkeypatch.setattr(app, "_show_jarldome_editor", lambda parent, node: None)

    app.show_node_view(app.world_data["nodes"]["4"])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    texts = _descendant_texts(presentation_frame)
    assert {
        "Sammanfattning",
        "Undernoder",
        "Arbete/DV",
        "Lager",
        "Soldater",
        "Umbärande",
    }.issubset(texts)
    assert not _descendants_of_type(
        presentation_frame, (ttk.Entry, ttk.Combobox, ttk.Spinbox)
    )


def test_domain_overview_handles_missing_optional_values(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    monkeypatch.setattr(app, "_show_jarldome_editor", lambda parent, node: None)

    app.show_node_view(app.world_data["nodes"]["4"])

    notebook = _find_notebook(app.details_panel.body)
    presentation_frame = notebook.nametowidget(notebook.tabs()[1])
    assert "Saknas ännu" in _descendant_texts(presentation_frame)


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
        "Skatt",
        "Soldater",
        "Status & risk",
        "Flaggor",
        "Åtgärder",
    }.issubset(texts)
    assert not _descendants_of_type(
        presentation_frame, (ttk.Entry, ttk.Combobox, ttk.Spinbox)
    )


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
