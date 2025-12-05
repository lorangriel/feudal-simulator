import tkinter as tk
from tkinter import messagebox

import pytest

from src.ui import app as ui_app
from src.world_manager import AssignResult


def _build_world(owner_level: str = "none", owner_id: int | None = None):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2], "name": "Sveariket"},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "name": "Uppland"},
            "3": {"node_id": 3, "parent_id": 2, "children": [4], "name": "Attundaland"},
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


def test_owner_selection_commits_and_updates_status(root):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
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
    assert any("Ägare uppdaterad" in msg for msg in app.status_service.messages)


def test_owner_selection_reverts_on_failure(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = _build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    initial_label = app.details_panel.ownership_var.get()
    error_calls: list[tuple] = []

    def _fail_assign(_province_id, _owner_anchor):
        return AssignResult(False, "Testfel")

    def _capture_error(*args, **kwargs):
        error_calls.append(args)

    monkeypatch.setattr(app.world_manager, "assign_personal_owner", _fail_assign)
    monkeypatch.setattr(messagebox, "showerror", _capture_error)

    owner_label = f"Furstendömet {app.get_display_name(2)}"
    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    node = app.world_data["nodes"]["4"]
    assert node.get("owner_assigned_level", "none") == "none"
    assert app.details_panel.ownership_var.get() == initial_label
    assert error_calls
