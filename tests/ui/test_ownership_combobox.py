import tkinter as tk
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
    assert app.details_panel.ownership_var.get() == "Lokal ägo"


def test_valid_assignment_updates_metadata(root):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    ownership_label = "Furste (nivå 1)"
    app.details_panel.ownership_combobox.set(ownership_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    node = app.world_data["nodes"]["4"]
    assert node["owner_assigned_level"] == "1"
    assert node["owner_assigned_id"] == 2
    assert node["personal_province_path"] == [1, 2]


def test_province_view_refreshes_on_removal(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_level="1", owner_id=2)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    app.details_panel.ownership_combobox.set("Lokal ägo")
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    assert app.world_data["nodes"]["4"]["owner_assigned_level"] == "none"
    assert app.world_data["nodes"]["4"].get("owner_assigned_id") is None
    assert app.world_data["nodes"]["4"].get("personal_province_path") == []


def test_same_owner_selection_reverts(root, monkeypatch):
    errors: list[tuple] = []
    app = ui_app.create_app(root)

    def _capture_error(*args, **kwargs):
        errors.append(args)

    app.world_data = build_world(owner_level="1", owner_id=2)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()
    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    current_label = app.details_panel.ownership_var.get()
    app.tooltip_manager.hide_tooltip(app.details_panel.ownership_combobox)
    app.tooltip_manager.hide_tooltip(app.details_panel.ownership_frame)
    monkeypatch.setattr(messagebox, "showerror", _capture_error)
    app.details_panel.ownership_combobox.set(current_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    node = app.world_data["nodes"]["4"]
    assert node["owner_assigned_level"] == "1"
    assert node["owner_assigned_id"] == 2
    assert not errors
