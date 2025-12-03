import tkinter as tk
from tkinter import messagebox

import pytest

from src.ui import app as ui_app


@pytest.fixture
def root(monkeypatch):
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    r.withdraw()
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: None)
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


def build_world(owner_level: str = "none", owner_id: int | None = None):
    return {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [2],
                "name": "Sveariket",
            },
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [3],
                "name": "Uppland",
            },
            "3": {
                "node_id": 3,
                "parent_id": 2,
                "children": [4],
                "name": "Attundaland",
            },
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "children": [],
                "custom_name": "Testdalen",
                "owner_assigned_level": owner_level,
                "owner_assigned_id": owner_id,
                "personal_province_path": [1, 2] if owner_level != "none" else [],
            },
        }
    }


def test_combobox_visible_and_prefilled(root):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    assert app.details_panel.ownership_frame.winfo_manager()
    assert app.details_panel.ownership_var.get() == "Lokal ägo (default)"


def test_valid_assignment_updates_metadata_and_province_view(root):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.structure_panel.update_mode("province")
    app.current_province_owner_id = 2

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    owner_label = f"Furstendömet {app.get_display_name(2)}"
    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    node = app.world_data["nodes"]["4"]
    assert node["owner_assigned_level"] == "1"
    assert node["owner_assigned_id"] == 2
    assert node["personal_province_path"]
    assert "4" in app.tree.get_children()


def test_invalid_assignment_shows_error_and_reverts(root, monkeypatch):
    errors: list[tuple] = []
    app = ui_app.create_app(root)

    def _capture_error(*args, **kwargs):
        errors.append(args)

    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    initial_label = app.details_panel.ownership_var.get()
    owner_label = f"Furstendömet {app.get_display_name(2)}"
    monkeypatch.setattr(app, "_ownership_lineage_for_node", lambda _node_id: [1, 1])
    monkeypatch.setattr(messagebox, "showerror", _capture_error)

    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    node = app.world_data["nodes"]["4"]
    assert node["owner_assigned_level"] == "none"
    assert node.get("owner_assigned_id") is None
    assert node.get("personal_province_path") == []
    assert app.details_panel.ownership_var.get() == initial_label
    assert errors
