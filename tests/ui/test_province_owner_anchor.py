import tkinter as tk

import pytest

from src.feodal_simulator import FeodalSimulator
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


def build_world_with_jarldom(owner_name: str):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "name": owner_name},
            "3": {"node_id": 3, "parent_id": 2, "children": [4]},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "children": [5],
                "owner_assigned_level": "1",
                "owner_assigned_id": 2,
                "name": "Jarldöme 4",
            },
            "5": {
                "node_id": 5,
                "parent_id": 4,
                "children": [],
                "owner_assigned_level": "1",
                "owner_assigned_id": 2,
                "name": "Underprovins",
            },
        },
        "characters": {},
    }


def build_world_without_jarldom(owner_name: str):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [], "name": owner_name},
        },
        "characters": {},
    }


def test_anchor_wraps_province_subtree(root):
    app = ui_app.create_app(root)
    app.world_data = build_world_with_jarldom(owner_name="Ägarnamn")
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    anchor = FeodalSimulator.PROVINCE_ANCHOR_IID

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.on_tree_selection_change()

    app.structure_panel.show_personal_button.invoke()

    assert app.tree.get_children("") == (anchor,)
    assert app.tree.item(anchor, "text") == "Ägare: Ägarnamn (nivå 1)"
    assert app.tree.get_children(anchor) == ("4",)
    assert app.tree.get_children("4") == ("5",)


def test_anchor_renders_without_subtree(root):
    app = ui_app.create_app(root)
    app.world_data = build_world_without_jarldom(owner_name="Tomt ägande")
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    anchor = FeodalSimulator.PROVINCE_ANCHOR_IID

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.on_tree_selection_change()

    app.structure_panel.show_personal_button.invoke()

    assert app.tree.get_children("") == (anchor,)
    assert app.tree.get_children(anchor) == ()
    assert app.tree.item(anchor, "text") == "Ägare: Tomt ägande (nivå 1)"
