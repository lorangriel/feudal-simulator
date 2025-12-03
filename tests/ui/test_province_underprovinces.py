import tkinter as tk

import pytest

from src.ui import app as ui_app


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    r.withdraw()
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


def build_world(owner_id: int):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "children": [3],
                "owner_assigned_level": "1",
                "owner_assigned_id": owner_id,
            },
            "3": {"node_id": 3, "parent_id": 2, "children": [4]},
            "4": {"node_id": 4, "parent_id": 3, "children": []},
        },
        "characters": {},
    }


def test_province_view_includes_underprovinces(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_id=2)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.on_tree_selection_change()

    app.structure_panel.show_personal_button.invoke()

    assert app.tree.get_children("") == ("2",)
    assert app.tree.get_children("2") == ("3",)
    assert app.tree.get_children("3") == ("4",)

    app.exit_province_view()
    app.world_data["nodes"]["3"]["owner_assigned_level"] = "1"
    app.world_data["nodes"]["3"]["owner_assigned_id"] = 3

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.on_tree_selection_change()
    app.structure_panel.show_personal_button.invoke()

    assert app.tree.get_children("") == ("2",)
    assert app.tree.get_children("2") == ()

    app.exit_province_view()
    app.tree.selection_set("3")
    app.tree.focus("3")
    app.on_tree_selection_change()
    app.structure_panel.show_personal_button.invoke()

    assert app.tree.get_children("") == ("3",)
    assert app.tree.get_children("3") == ("4",)
